"""PWR-022: selectively clear the current queue at damage-action boundaries.

Expectations come from GameActionManager.clearPostCombatActions, not a blanket
ban on actions queued after the last enemy dies. Card tests use PlayCardAction.
"""

import pytest

from actions.card import DrawCardsAction
from actions.card_play_lifecycle import queue_card_play
from actions.combat import GainEnergyAction
from actions.combat_cards import PlayCardAction
from actions.combat_damage import DealDamageAction, GainBlockAction, HealAction, LoseHPAction
from actions.orb import EvokeAllOrbsAction, EvokeOrbAction, OrbEvokeAction, OrbPassiveAction
from cards.ironclad.defend import Defend
from cards.ironclad.pommel_strike import PommelStrike
from cards.ironclad.reaper import Reaper
from cards.watcher.wallop import Wallop
from enemies.act1.cultist import Cultist
from enemies.act3.darkling import Darkling
from engine.messages import CreatureDiedMessage, EnemyHpDepletedMessage
from orbs.frost import FrostOrb
from orbs.lightning import LightningOrb
from orbs.plasma import PlasmaOrb
from powers.definitions.corpse_explosion import CorpseExplosionPower
from tests.test_combat_utils import create_test_helper
from utils.types import DamageType


def setup_combat(*enemies):
    helper = create_test_helper()
    helper.create_player(hp=40, max_hp=100, energy=30)
    helper.game_state.player.base_draw_count = 0
    helper.start_combat(list(enemies))
    for _ in range(3):
        helper.add_card_to_draw_pile(Defend())
    return helper


def play(helper, card):
    helper.add_card_to_hand(card)
    helper.game_state.add_action(PlayCardAction(card))
    helper.game_state.drive_actions()


@pytest.mark.parametrize("upgraded", [False, True])
@pytest.mark.parametrize("last_enemy", [False, True])
def test_pommel_strike_draw_is_cancelled_only_when_combat_finishes(upgraded, last_enemy):
    target = Cultist()
    helper = setup_combat(target, *([] if last_enemy else [Cultist()]))
    target.hp = 1
    card = PommelStrike()
    if upgraded:
        card.upgrade()
    play(helper, card)

    expected_draw = 0 if last_enemy else (2 if upgraded else 1)
    piles = helper.game_state.player.card_manager.piles
    assert target.is_dead()
    assert len(piles["hand"]) == expected_draw
    assert len(piles["draw_pile"]) == 3 - expected_draw
    assert card in piles["discard_pile"]
    assert card not in piles["limbo"]
    assert helper.game_state.active_card_plays == []


@pytest.mark.parametrize("kill_kind", ["attack", "hp_loss"])
@pytest.mark.parametrize("last_enemy", [False, True])
def test_mixed_queue_retains_healing_block_and_damage_only(kill_kind, last_enemy):
    target = Cultist()
    helper = setup_combat(target, *([] if last_enemy else [Cultist()]))
    gs = helper.game_state
    player = gs.player
    target.hp = 1
    kill = (DealDamageAction(1, target=target, source=player)
            if kill_kind == "attack" else LoseHPAction(1, target=target))
    gs.add_actions([
        kill,
        DrawCardsAction(count=1),
        GainEnergyAction(energy=2),
        HealAction(amount=7, target=player),
        GainBlockAction(block=5, target=player),
        DealDamageAction(3, target=player, damage_type=DamageType.THORNS),
        LoseHPAction(2, target=player),
    ])
    gs.drive_actions()

    assert target.is_dead()
    assert player.hp == 45
    assert player.block == 2
    assert len(player.card_manager.piles["hand"]) == (0 if last_enemy else 1)
    assert player.energy == (30 if last_enemy else 32)
    assert gs.action_queue.is_empty()


def test_retained_action_can_enqueue_new_nonretained_actions_after_cleanup():
    target = Cultist()
    helper = setup_combat(target)
    gs = helper.game_state
    target.hp = 1

    class HealAndQueue(HealAction):
        # A component probe: real healing delegates unchanged, then constructs
        # fresh actions after the one-shot clearPostCombatActions boundary.
        def execute(self):
            super().execute()
            gs.add_actions([DrawCardsAction(count=1), GainEnergyAction(energy=2)])

    gs.add_actions([
        LoseHPAction(1, target=target),
        DrawCardsAction(count=1),
        GainEnergyAction(energy=8),
        HealAndQueue(amount=7, target=gs.player),
    ])
    gs.drive_actions()

    assert gs.player.hp == 47
    assert gs.player.energy == 32
    assert len(gs.player.card_manager.piles["hand"]) == 1
    assert len(gs.player.card_manager.piles["draw_pile"]) == 2


@pytest.mark.parametrize("damage_kind", ["damage", "hp_loss"])
def test_later_retained_damage_performs_its_own_cleanup_boundary(damage_kind):
    target = Cultist()
    helper = setup_combat(target)
    gs = helper.game_state
    target.hp = 1

    class HealAndQueueDamage(HealAction):
        def execute(self):
            super().execute()
            later_damage = (LoseHPAction(1, target=gs.player)
                            if damage_kind == "hp_loss" else
                            DealDamageAction(1, target=gs.player, damage_type=DamageType.THORNS))
            gs.add_actions([later_damage, DrawCardsAction(count=1), GainEnergyAction(energy=2)])

    # Each original DamageAction/LoseHPAction checks whether all monsters are
    # dead after damage. New ordinary actions survive until another such check.
    gs.add_actions([LoseHPAction(1, target=target), HealAndQueueDamage(amount=7, target=gs.player)])
    gs.drive_actions()

    assert gs.player.hp == 46
    assert gs.player.energy == 30
    assert len(gs.player.card_manager.piles["hand"]) == 0
    assert len(gs.player.card_manager.piles["draw_pile"]) == 3


@pytest.mark.parametrize("card_class", [Wallop, Reaper])
def test_native_finishing_card_keeps_block_healing_and_card_finalization(card_class):
    target = Cultist()
    helper = setup_combat(target)
    target.hp = 1
    card = card_class()
    play(helper, card)

    player = helper.game_state.player
    assert target.is_dead()
    # CARD-035 separately tracks overkill amount; here we only establish that
    # the native reward action survives and the active card finalizes once.
    if card_class is Wallop:
        assert player.block > 0
        expected_pile = "discard_pile"
    else:
        assert player.hp > 40
        expected_pile = "exhaust_pile"
    assert player.card_manager.piles[expected_pile].count(card) == 1
    assert card not in player.card_manager.piles["limbo"]
    assert helper.game_state.active_card_plays == []


@pytest.mark.parametrize("kill_kind", ["attack", "hp_loss"])
def test_corpse_explosion_chain_preserves_damage_and_clears_on_final_death(kill_kind, monkeypatch):
    enemies = [Cultist(), Cultist(), Cultist()]
    helper = setup_combat(*enemies)
    gs = helper.game_state
    for enemy in enemies:
        enemy._max_hp = 10
        enemy.hp = 1
        enemy.add_power(CorpseExplosionPower(owner=enemy))
    events = []
    publish = gs.publish_message

    def observe(message, *args, **kwargs):
        events.append(message)
        return publish(message, *args, **kwargs)

    monkeypatch.setattr(gs, "publish_message", observe)
    kill = (DealDamageAction(1, target=enemies[0], source=gs.player)
            if kill_kind == "attack" else LoseHPAction(1, target=enemies[0]))
    # The first collapse queues its explosion behind the ordinary actions.
    # They execute before the final death and are not retroactively undone.
    gs.add_actions([kill, GainEnergyAction(energy=2)])
    gs.drive_actions()
    assert all(enemy.is_dead() for enemy in enemies)
    assert gs.player.energy == 32
    for enemy in enemies:
        assert sum(isinstance(m, EnemyHpDepletedMessage) and m.creature is enemy
                   for m in events) == 1
        assert sum(isinstance(m, CreatureDiedMessage) and m.creature is enemy
                   for m in events) == 1
    assert gs.action_queue.is_empty()


@pytest.mark.parametrize("last", [False, True])
def test_fungi_beast_death_debuff_is_removed_only_on_final_kill(last):
    from enemies.act1.fungi_beast import FungiBeast

    enemy, anchor = FungiBeast(), Cultist()
    helper = setup_combat(enemy) if last else setup_combat(enemy, anchor)
    enemy.hp = 1
    helper.game_state.add_action(DealDamageAction(5, target=enemy, source=helper.game_state.player))
    helper.game_state.drive_actions()
    assert helper.game_state.player.has_power("Vulnerable") is (not last)


@pytest.mark.parametrize("enemy_class", [Cultist, Darkling])
def test_last_enemy_death_cancels_pending_autoplay_but_finalizes_its_card(enemy_class):
    target = enemy_class()
    helper = setup_combat(target)
    gs = helper.game_state
    target.hp = 1
    pending = Defend()
    helper.add_card_to_hand(pending)
    queue_card_play(pending)
    gs.add_action(LoseHPAction(1, target=target))
    gs.drive_actions()

    assert target.is_dead()
    assert gs.player.block == 0
    assert gs.pending_card_plays == []
    assert gs.player.card_manager.piles["discard_pile"].count(pending) == 1
    assert pending not in gs.player.card_manager.piles["limbo"]


@pytest.mark.parametrize("orb_class", [FrostOrb, PlasmaOrb])
@pytest.mark.parametrize("evoke_kind", ["one", "all", "resolved"])
def test_damage_typed_orb_evoke_survives_and_can_create_new_reward_actions(orb_class, evoke_kind):
    target = Cultist()
    helper = setup_combat(target)
    gs = helper.game_state
    target.hp = 1
    orb = orb_class()
    if evoke_kind == "resolved":
        evoke = OrbEvokeAction(orb)
    else:
        gs.player.orb_manager.add_orb(orb)
        evoke = EvokeOrbAction() if evoke_kind == "one" else EvokeAllOrbsAction()
    # Original EvokeOrbAction/EvokeAllOrbsAction are DAMAGE, including when the
    # orb produces energy instead of damage. OrbEvokeAction is their split tail.
    gs.add_actions([LoseHPAction(1, target=target), evoke, GainEnergyAction(energy=8)])
    gs.drive_actions()

    assert target.is_dead()
    assert gs.player.orb_manager.get_orb_count() == 0
    assert gs.player.block == (5 if orb_class is FrostOrb else 0)
    assert gs.player.energy == (32 if orb_class is PlasmaOrb else 30)


@pytest.mark.parametrize("orb_class", [FrostOrb, LightningOrb, PlasmaOrb])
def test_passive_wrapper_maps_block_damage_and_energy_cleanup_separately(orb_class, monkeypatch):
    target = Cultist()
    helper = setup_combat(target)
    gs = helper.game_state
    target.hp = 1
    orb = orb_class()
    calls = []
    native = orb.on_passive

    def observe():
        calls.append(orb)
        return native()

    # Component input for the split wrapper; delegate the native orb effect.
    # Lightning has no remaining target, so count dispatch without faking one.
    monkeypatch.setattr(orb, "on_passive", observe)
    gs.add_actions([LoseHPAction(1, target=target), OrbPassiveAction(orb)])
    gs.drive_actions()

    assert len(calls) == (0 if orb_class is PlasmaOrb else 1)
    assert gs.player.block == (2 if orb_class is FrostOrb else 0)
    assert gs.player.energy == 30
