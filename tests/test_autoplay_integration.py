"""Real producer chains for the free-cost boundary and nested cancellation."""
import pytest

from actions.card import DrawCardsAction
from actions.combat_cards import PlayCardAction
from actions.combat_status import UsePotionAction
from cards.colorless.forethought import Forethought
from cards.ironclad.defend import Defend
from cards.ironclad.havoc import Havoc
from cards.ironclad.heavy_blade import HeavyBlade
from cards.ironclad.strike import Strike
from cards.silent.setup import Setup
from cards.watcher.conclude import Conclude
from enemies.act1.cultist import Cultist
from enemies.act3.awakened_one import AwakenedOne
from engine.messages import CardPlayedMessage, DamageDealtMessage
from potions.global_potions import DistilledChaos
from relics.global_relics.event import Necronomicon
from tests.test_combat_utils import create_test_helper


def prepare(monkeypatch, enemy=None, energy=6):
    helper = create_test_helper()
    player = helper.create_player(hp=100, max_hp=100, energy=energy)
    player.base_draw_count = 0
    enemy = enemy or Cultist()
    enemy._max_hp = 300
    enemy.hp = 300
    combat = helper.start_combat([enemy])
    assert helper.game_state.drive_actions() is None
    messages = []
    original = helper.game_state.publish_message

    def publish(message, *args, **kwargs):
        messages.append(message)
        return original(message, *args, **kwargs)

    monkeypatch.setattr(helper.game_state, "publish_message", publish)
    return helper, player, enemy, combat, messages


@pytest.mark.parametrize("producer", [Forethought, Setup])
def test_real_single_free_cost_chain_does_not_consume_necronomicon(producer, monkeypatch):
    helper, player, enemy, _, messages = prepare(monkeypatch)
    relic = Necronomicon()
    player.relics.append(relic)
    heavy, preparation = HeavyBlade(), producer()
    helper.add_card_to_hand(heavy)
    helper.add_card_to_hand(preparation)
    helper.game_state.add_action(PlayCardAction(preparation))
    assert helper.game_state.drive_actions() is None
    assert player.card_manager.get_card_location(heavy) == "draw_pile"
    assert heavy.cost == 0
    helper.game_state.add_action(DrawCardsAction(count=1))
    assert helper.game_state.drive_actions() is None
    assert player.card_manager.get_card_location(heavy) == "hand"
    helper.game_state.add_action(PlayCardAction(heavy))
    assert helper.game_state.drive_actions() is None
    assert enemy.hp == 286
    assert not relic.double_attack_played
    assert heavy.cost == 2
    assert [m.card for m in messages if isinstance(m, CardPlayedMessage)] == [preparation, heavy]


def test_real_conclude_cancels_nested_havoc_before_it_can_produce_another_card(monkeypatch):
    helper, player, enemy, combat, messages = prepare(monkeypatch, energy=0)
    extra, defense, havoc, conclude = Defend(), Defend(), Havoc(), Conclude()
    player.card_manager.piles["draw_pile"] = [extra, defense, havoc, conclude]
    potion = DistilledChaos()
    player.potions.append(potion)
    helper.game_state.add_action(UsePotionAction(potion, target=player))
    assert helper.game_state.drive_actions() is None
    assert [m.card for m in messages if isinstance(m, CardPlayedMessage)] == [conclude]
    assert enemy.hp == 288 and player.block == 0
    assert combat.combat_state.current_phase == "player_end"
    assert player.card_manager.get_card_location(extra) == "draw_pile"
    assert all(player.card_manager.get_card_location(card) == "discard_pile"
               for card in [conclude, havoc, defense])
    assert not helper.game_state.pending_card_plays


def test_automatic_targeted_attack_without_living_target_is_cancelled(monkeypatch):
    helper, player, enemy, _, messages = prepare(monkeypatch, enemy=AwakenedOne())
    enemy.hp = 0  # Prepared half-dead enemy isolates the no-target contract.
    assert enemy.half_dead
    card = Strike()
    player.card_manager.piles["draw_pile"] = [card]
    potion = DistilledChaos()
    player.potions.append(potion)
    helper.game_state.add_action(UsePotionAction(potion, target=player))
    assert helper.game_state.drive_actions() is None
    assert not any(isinstance(m, (CardPlayedMessage, DamageDealtMessage)) for m in messages)
    assert player.card_manager.get_card_location(card) == "discard_pile"
    assert not helper.game_state.pending_card_plays and not helper.game_state.active_card_plays
