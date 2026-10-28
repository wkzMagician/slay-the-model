"""PWR-024/CARD-048: real lethal plays and cancellable turn-end card uses."""
import pytest

from actions.combat import DealDamageAction, LoseHPAction
from actions.combat import EndTurnAction
from actions.combat_cards import PlayCardAction
from actions.combat_cards import PlayCardBHAction
from cards.colorless.burn import Burn
from cards.base import Card
from cards.colorless.decay import Decay
from cards.colorless.regret import Regret
from cards.colorless.doubt import Doubt
from cards.colorless.shame import Shame
from cards.ironclad.hemokinesis import Hemokinesis
from enemies.act1.cultist import Cultist
from engine.messages import CombatEndedMessage
from orbs.lightning import LightningOrb
from potions.global_potions import FairyInABottle
from powers.definitions.juggernaut import JuggernautPower
from powers.definitions.metallicize import MetallicizePower
from powers.definitions.self_repair import SelfRepairPower
from relics.character.ironclad import BlackBlood, BurningBlood
from relics.global_relics.rare import LizardTail
from relics.global_relics.event import MarkOfBloom
from tests.test_combat_utils import create_test_helper
from utils.result_types import GameTerminalState


def setup(hp=2, enemy_hp=1):
    helper = create_test_helper()
    player = helper.create_player(max_hp=100, hp=hp)
    enemy = helper.create_enemy(Cultist, hp=enemy_hp)
    combat = helper.start_combat([enemy])
    helper.game_state.drive_actions()
    return helper.game_state, player, enemy, combat


@pytest.mark.parametrize("recovery", ["none", "blood", "black", "repair"])
def test_lethal_hemokinesis_does_not_kill_target_or_publish_victory(recovery, monkeypatch):
    gs, player, enemy, combat = setup()
    if recovery == "blood":
        player.relics.append(BurningBlood())
    elif recovery == "black":
        player.relics.append(BlackBlood())
    elif recovery == "repair":
        player.add_power(SelfRepairPower(amount=7, owner=player))
    events = []
    native = gs.publish_message

    def publish(msg):
        events.append(msg)
        return native(msg)

    monkeypatch.setattr(gs, "publish_message", publish)
    card = Hemokinesis()
    player.card_manager.piles["hand"] = [card]
    gs.add_action(PlayCardBHAction(card, [enemy]))
    result = gs.drive_actions()
    assert result == GameTerminalState.GAME_LOSE
    assert player.hp == 0
    assert enemy.hp == 1
    assert combat._check_combat_end() == GameTerminalState.GAME_LOSE
    assert not any(isinstance(event, CombatEndedMessage) for event in events)


def test_real_death_action_survives_last_enemy_cleanup():
    gs, player, enemy, combat = setup()
    # Separate producer: already-created damage remains valid after enemy death.
    gs.add_actions([DealDamageAction(1, enemy), LoseHPAction(amount=2)])
    assert gs.drive_actions() == GameTerminalState.GAME_LOSE
    assert player.hp == 0 and enemy.hp == 0
    assert combat._check_combat_end() == GameTerminalState.GAME_LOSE


@pytest.mark.parametrize("hp", [3, 90])
@pytest.mark.parametrize("recovery,healing", [(BurningBlood, 6), (BlackBlood, 12)])
def test_surviving_hemokinesis_still_wins_and_heals(hp, recovery, healing):
    gs, player, enemy, combat = setup(hp=hp)
    player.relics.append(recovery())
    card = Hemokinesis()
    player.card_manager.piles["hand"] = [card]
    gs.add_action(PlayCardBHAction(card, [enemy]))
    assert gs.drive_actions() is None
    assert combat._check_combat_end() == GameTerminalState.COMBAT_WIN
    assert player.hp == min(100, hp - 2 + healing)


@pytest.mark.parametrize("save", ["none", "fairy", "tail"])
@pytest.mark.parametrize("orbs", [1, 2])
def test_orb_victory_cancels_burns_without_spending_saves(save, orbs):
    gs, player, enemy, combat = setup(hp=1, enemy_hp=3 * orbs)
    fairy = FairyInABottle()
    tail = LizardTail()
    if save == "fairy":
        player.potions.append(fairy)
    elif save == "tail":
        player.relics.append(tail)
    player.orb_manager.orbs[:] = [LightningOrb() for _ in range(orbs)]
    burns: list[Card] = [Burn(), Burn()]
    burns[1].upgrade()
    player.card_manager.piles["hand"] = burns
    assert combat._end_player_phase() is None
    assert combat._check_combat_end() == GameTerminalState.COMBAT_WIN
    assert player.hp == 1
    assert (fairy in player.potions) == (save == "fairy")
    assert tail.can_revive


def test_block_reaction_victory_also_cancels_unstarted_burn():
    gs, player, enemy, combat = setup(hp=100, enemy_hp=5)
    player.add_power(MetallicizePower(amount=3, owner=player))
    player.add_power(JuggernautPower(amount=5, owner=player))
    burn = Burn()
    burn.upgrade()
    player.card_manager.piles["hand"] = [burn]
    combat._end_player_phase()
    assert enemy.hp == 0
    assert player.hp == 100 and player.block == 3


def test_burn_still_hurts_when_an_enemy_remains():
    gs, player, enemy, combat = setup(hp=10, enemy_hp=30)
    player.orb_manager.orbs[:] = [LightningOrb()]
    player.card_manager.piles["hand"] = [Burn()]
    combat._end_player_phase()
    assert enemy.hp == 27
    assert player.hp == 8


@pytest.mark.parametrize("curse", [Decay, Regret, Doubt, Shame])
@pytest.mark.parametrize("clears", [False, True])
def test_shared_end_turn_card_queue_preserves_surviving_effects(curse, clears):
    gs, player, enemy, combat = setup(hp=10, enemy_hp=3 if clears else 30)
    player.orb_manager.orbs[:] = [LightningOrb()]
    player.card_manager.piles["hand"] = [curse()]
    combat._end_player_phase()
    damage = 0 if clears else 2 if curse is Decay else 1 if curse is Regret else 0
    assert player.hp == 10 - damage
    if curse in [Doubt, Shame]:
        assert bool(player.powers) == (not clears)


@pytest.mark.parametrize("save,expected", [("fairy", 30), ("tail", 50), ("both", 30)])
def test_hemokinesis_revives_before_attacking(save, expected):
    gs, player, enemy, combat = setup()
    fairy = FairyInABottle()
    tail = LizardTail()
    if save in ["fairy", "both"]:
        player.potions.append(fairy)
    if save in ["tail", "both"]:
        player.relics.append(tail)
    card = Hemokinesis()
    player.card_manager.piles["hand"] = [card]
    gs.add_action(PlayCardBHAction(card, [enemy]))
    assert gs.drive_actions() is None
    assert enemy.hp == 0 and player.hp == expected
    assert combat._check_combat_end() == GameTerminalState.COMBAT_WIN
    assert tail.can_revive == (save != "tail")


def test_bloom_prevents_hemokinesis_revival_and_victory():
    gs, player, enemy, combat = setup()
    fairy = FairyInABottle()
    player.potions.append(fairy)
    player.relics.extend([LizardTail(), MarkOfBloom(), BurningBlood()])
    card = Hemokinesis()
    player.card_manager.piles["hand"] = [card]
    gs.add_action(PlayCardBHAction(card, [enemy]))
    assert gs.drive_actions() == GameTerminalState.GAME_LOSE
    assert player.hp == 0 and enemy.hp == 1
    assert fairy in player.potions


@pytest.mark.parametrize("scenario", ["hemokinesis", "orb_burn"])
def test_native_combat_start_returns_correct_terminal(scenario, monkeypatch):
    gs, player, enemy, combat = setup(hp=2 if scenario == "hemokinesis" else 1,
                                      enemy_hp=1 if scenario == "hemokinesis" else 3)
    player.base_draw_count = 2
    player.card_manager.piles["deck"] = [Hemokinesis()] if scenario == "hemokinesis" else [Burn(), Burn()]

    def choose(req):
        if scenario == "orb_burn":
            player.orb_manager.orbs[:] = [LightningOrb()]
        action_type = PlayCardAction if scenario == "hemokinesis" else EndTurnAction
        index = next((i for i, option in enumerate(req.options)
                      if any(isinstance(action, action_type) for action in option.actions)), 0)
        return gs._build_submission(req.options, [index])

    monkeypatch.setattr(gs, "resolve_input_request", choose)
    assert combat.start() == (GameTerminalState.GAME_LOSE if scenario == "hemokinesis"
                              else GameTerminalState.COMBAT_WIN)
    assert player.hp == (0 if scenario == "hemokinesis" else 1)
