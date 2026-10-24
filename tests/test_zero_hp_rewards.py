"""REL-021/CARD-033: original GremlinHorn.onMonsterDeath/SunderAction rules.

Prepared combat states use real card/action effects. Java source supplies the
expected results; these tests do not claim an original-game runtime comparison.
"""

import pytest

from actions.combat_cards import PlayCardAction
from actions.combat_damage import LoseHPAction
from cards.defect.sunder import Sunder, SunderDamageAction
from cards.colorless.hand_of_greed import HandOfGreed
from cards.ironclad.defend import Defend
from cards.ironclad.feed import Feed
from cards.ironclad.strike import Strike
from cards.silent.deadly_poison import DeadlyPoison
from enemies.act1.cultist import Cultist
from enemies.act3.awakened_one import AwakenedOne
from enemies.act3.darkling import Darkling
from powers.definitions.corpse_explosion import CorpseExplosionPower
from powers.definitions.strength import StrengthPower
from relics.global_relics.uncommon import GremlinHorn
from tests.test_combat_utils import create_test_helper
from utils.types import DamageType


def prepare(enemy_class=Cultist, *, last=False, horn=False):
    helper = create_test_helper()
    player = helper.create_player(hp=500, max_hp=500, energy=30)
    player.base_draw_count = 0
    target = enemy_class()
    anchor = Darkling() if enemy_class is Darkling else Cultist()
    combat = helper.start_combat([target] if last else [target, anchor])
    helper.game_state.drive_actions()
    target._max_hp = 20
    target.hp = 1
    anchor._max_hp = 500
    anchor.hp = 500
    if horn:
        player.relics.append(GremlinHorn())
    for _ in range(12):
        helper.add_card_to_draw_pile(Defend())
    return helper, player, target, anchor, combat


def play(helper, card):
    helper.add_card_to_hand(card)
    helper.game_state.add_action(PlayCardAction(card))
    helper.game_state.drive_actions()


@pytest.mark.parametrize("enemy_class", [Cultist, AwakenedOne, Darkling])
@pytest.mark.parametrize("kind", ["attack", "hp_loss", "poison"])
def test_horn_rewards_each_nonfinal_collapse_for_every_damage_path(enemy_class, kind):
    helper, player, target, _, _ = prepare(enemy_class, horn=True)
    if kind == "attack":
        play(helper, Strike())
        expected_energy = 30
    elif kind == "hp_loss":
        helper.game_state.add_action(LoseHPAction(amount=1, target=target))
        helper.game_state.drive_actions()
        expected_energy = 31
    else:
        play(helper, DeadlyPoison())
        # Genuine poison effect, inspected before the enemy's next action.
        poison = target.get_power("Poison")
        assert poison is not None
        poison.on_turn_start()
        helper.game_state.drive_actions()
        expected_energy = 30
    assert target.hp <= 0
    assert player.energy == expected_energy
    assert len(player.card_manager.piles["hand"]) == 1
    # Later damage against the same zero-HP state must not repeat the reward.
    helper.game_state.add_action(LoseHPAction(amount=1, target=target))
    helper.game_state.drive_actions()
    assert player.energy == expected_energy
    assert len(player.card_manager.piles["hand"]) == 1


@pytest.mark.parametrize("enemy_class", [Cultist, Darkling])
@pytest.mark.parametrize("kind", ["attack", "hp_loss", "poison"])
def test_horn_does_not_reward_basic_all_dead(enemy_class, kind):
    helper, player, target, _, _ = prepare(enemy_class, last=True, horn=True)
    if kind == "attack":
        play(helper, Strike())
    elif kind == "hp_loss":
        helper.game_state.add_action(LoseHPAction(amount=1, target=target))
        helper.game_state.drive_actions()
    else:
        play(helper, DeadlyPoison())
        poison = target.get_power("Poison")
        assert poison is not None
        poison.on_turn_start()
        helper.game_state.drive_actions()
    assert target.is_dead()
    assert player.energy == (30 if kind == "hp_loss" else 29)
    assert player.card_manager.piles["hand"] == []


@pytest.mark.parametrize("enemy_class", [Cultist, AwakenedOne, Darkling])
@pytest.mark.parametrize("upgraded", [False, True])
def test_sunder_refunds_zero_hp_when_combat_continues(enemy_class, upgraded):
    helper, player, target, _, _ = prepare(enemy_class)
    card = Sunder()
    if upgraded:
        card.upgrade()
    play(helper, card)
    assert target.hp <= 0
    assert player.energy == 30


@pytest.mark.parametrize("enemy_class", [Cultist, AwakenedOne, Darkling])
@pytest.mark.parametrize("upgraded", [False, True])
def test_sunder_no_refund_for_surviving_target(enemy_class, upgraded):
    helper, player, target, _, _ = prepare(enemy_class)
    target._max_hp = 100
    target.hp = 100
    card = Sunder()
    if upgraded:
        card.upgrade()
    play(helper, card)
    assert target.hp == (68 if upgraded else 76)
    assert player.energy == 27


@pytest.mark.parametrize("enemy_class", [Cultist, Darkling])
@pytest.mark.parametrize("upgraded", [False, True])
def test_sunder_last_enemy_refund_is_removed_by_combat_cleanup(enemy_class, upgraded):
    helper, player, target, _, _ = prepare(enemy_class, last=True)
    card = Sunder()
    if upgraded:
        card.upgrade()
    play(helper, card)
    assert target.is_dead()
    assert player.energy == 27
    assert card in player.card_manager.piles["discard_pile"]


@pytest.mark.parametrize("enemy_class", [AwakenedOne, Darkling])
def test_feed_still_excludes_half_dead_while_sunder_refunds(enemy_class):
    helper, player, target, _, _ = prepare(enemy_class)
    max_hp = player.max_hp
    play(helper, Feed())
    assert target.half_dead
    assert player.max_hp == max_hp


def test_horn_corpse_explosion_rewards_only_before_final_cleanup():
    helper, player, target, anchor, _ = prepare(horn=True)
    # First collapse queues the explosion before relic gains; final collapse
    # then removes those gains. No reward survives the combat-ending chain.
    anchor.hp = 10
    target.add_power(CorpseExplosionPower(amount=1, owner=target))
    play(helper, Strike())
    assert target.is_dead() and anchor.is_dead()
    assert player.energy == 29
    assert player.card_manager.piles["hand"] == []


def test_horn_linked_group_finalization_does_not_reward_prior_half_dead_again():
    helper, player, first, second, _ = prepare(Darkling, horn=True)
    helper.game_state.add_action(LoseHPAction(amount=1, target=first))
    helper.game_state.drive_actions()
    assert player.energy == 31
    assert len(player.card_manager.piles["hand"]) == 1
    helper.game_state.add_action(LoseHPAction(amount=second.hp, target=second))
    helper.game_state.drive_actions()
    assert first.is_dead() and second.is_dead()
    assert player.energy == 31
    assert len(player.card_manager.piles["hand"]) == 1


def test_horn_is_not_triggered_by_player_hp_loss():
    helper, player, _, _, _ = prepare(horn=True)
    helper.game_state.add_action(LoseHPAction(amount=1, target=player))
    helper.game_state.drive_actions()
    assert player.energy == 30
    assert player.card_manager.piles["hand"] == []


@pytest.mark.parametrize("enemy_class", [Cultist, AwakenedOne, Darkling])
def test_horn_poison_reward_through_normal_enemy_phase(enemy_class):
    helper, player, target, _, combat = prepare(enemy_class, horn=True)
    play(helper, DeadlyPoison())
    assert player.energy == 29
    assert combat.execute_enemy_phase() is None
    assert player.energy == 30
    assert len(player.card_manager.piles["hand"]) == 1
    assert target.is_dead() or target.half_dead or (
        enemy_class is AwakenedOne and target._phase == 2
    )


@pytest.mark.parametrize("enemy_class", [AwakenedOne, Darkling])
def test_horn_rewards_new_collapse_after_normal_revival(enemy_class):
    helper, player, target, _, combat = prepare(enemy_class, horn=True)
    play(helper, Strike())
    assert player.energy == 30
    assert target.half_dead
    assert combat.execute_enemy_phase() is None
    combat._start_player_turn()
    helper.game_state.drive_actions()
    if enemy_class is Darkling:
        assert combat.execute_enemy_phase() is None
        combat._start_player_turn()
        helper.game_state.drive_actions()
    assert target.hp > 0 and not target.half_dead
    before_energy = player.energy
    before_hand = len(player.card_manager.piles["hand"])
    helper.game_state.add_action(LoseHPAction(amount=target.hp, target=target))
    helper.game_state.drive_actions()
    assert player.energy == before_energy + 1
    assert len(player.card_manager.piles["hand"]) == before_hand + 1


def test_lone_awakened_first_phase_is_not_basic_all_dead():
    helper, player, target, _, _ = prepare(AwakenedOne, last=True, horn=True)
    play(helper, Sunder())
    assert target.half_dead
    assert player.energy == 31  # Three refunded by Sunder and one from Horn.
    assert len(player.card_manager.piles["hand"]) == 1


@pytest.mark.parametrize("last", [False, True])
def test_sunder_awakened_phase_two_uses_normal_final_death_rules(last):
    helper, player, target, _, _ = prepare(AwakenedOne, last=last, horn=True)
    target._phase = 2  # Prepared phase-two input, not a revival-flow assertion.
    play(helper, Sunder())
    assert target.is_dead()
    assert player.energy == (27 if last else 31)


@pytest.mark.parametrize("blocked", [False, True])
def test_sunder_keeps_attack_damage_snapshot_and_runtime_block(blocked):
    helper, player, target, _, _ = prepare()
    target._max_hp = 100
    target.hp = 100
    player.add_power(StrengthPower(amount=3, owner=player))
    target.block = 100 if blocked else 0
    play(helper, Sunder())
    assert target.hp == (100 if blocked else 73)
    assert player.energy == 27


@pytest.mark.parametrize("invalid", ["zero_target", "dead_source"])
def test_sunder_cancelled_damage_cannot_create_refund(invalid):
    helper, player, target, _, _ = prepare()
    if invalid == "zero_target":
        target.hp = 0
    else:
        player.hp = 0
    # Explicit damage-action entry tests guards, not ordinary target selection.
    helper.game_state.add_action(SunderDamageAction(
        100, target, damage_type=DamageType.PHYSICAL, source=player,
    ))
    helper.game_state.drive_actions()
    assert player.energy == 30


@pytest.mark.parametrize("enemy_class", [Cultist, AwakenedOne, Darkling])
def test_horn_callback_follows_power_death_reaction_before_halfdead_cleanup(
    enemy_class, monkeypatch,
):
    helper, player, target, anchor, _ = prepare(enemy_class, horn=True)
    target.add_power(CorpseExplosionPower(amount=1, owner=target))
    seen = []
    original = helper.game_state.publish_message

    def publish(message, *args, **kwargs):
        if type(message).__name__ == "EnemyDefeatedMessage":
            seen.append((
                target.get_power("Corpse Explosion") is not None,
                [(type(action).__name__, getattr(action, "target", None),
                  getattr(action, "damage", None))
                 for action in helper.game_state.action_queue.queue],
            ))
        return original(message, *args, **kwargs)

    monkeypatch.setattr(helper.game_state, "publish_message", publish)
    play(helper, Strike())
    assert len(seen) == 1
    assert seen[0][0]
    assert ("DealDamageAction", anchor, 20) in seen[0][1]
    assert anchor.hp == 480
    assert player.energy == 30
    assert len(player.card_manager.piles["hand"]) == 1
    if enemy_class in (AwakenedOne, Darkling):
        assert target.get_power("Corpse Explosion") is None


@pytest.mark.parametrize("card_class", [Feed, HandOfGreed])
@pytest.mark.parametrize("upgraded", [False, True])
def test_fatal_rewards_are_applied_before_final_queue_cleanup(card_class, upgraded):
    helper, player, target, _, _ = prepare(last=True)
    before_max_hp, before_gold = player.max_hp, player.gold
    card = card_class()
    if upgraded:
        card.upgrade()
    play(helper, card)
    assert target.is_dead()
    if card_class is Feed:
        assert player.max_hp == before_max_hp + (4 if upgraded else 3)
        assert card in player.card_manager.piles["exhaust_pile"]
    else:
        assert player.gold == before_gold + (25 if upgraded else 20)
        assert card in player.card_manager.piles["discard_pile"]


@pytest.mark.parametrize("enemy_class", [AwakenedOne, Darkling])
@pytest.mark.parametrize("card_class", [Feed, HandOfGreed])
def test_synchronous_fatal_rewards_still_exclude_half_dead(enemy_class, card_class):
    helper, player, target, _, _ = prepare(enemy_class)
    before_max_hp, before_gold = player.max_hp, player.gold
    play(helper, card_class())
    assert target.half_dead
    assert player.max_hp == before_max_hp
    assert player.gold == before_gold
