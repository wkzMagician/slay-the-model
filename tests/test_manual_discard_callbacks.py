"""Exercise inherited discard subscriptions through real actions and phases."""
import pytest

from actions.card import DiscardCardAction, DrawCardsAction
from actions.combat_cards import PlayCardAction
from cards.silent.defend import Defend
from cards.silent.reflex import Reflex
from cards.silent.survivor import Survivor
from cards.silent.tactician import Tactician
from enemies.act1.cultist import Cultist
from player.player_factory import create_player
from tests.test_combat_utils import create_test_helper


@pytest.fixture
def combat_context():
    helper = create_test_helper()
    state = helper.game_state
    state.player = create_player('Silent')
    player = state.player
    player.relics = []
    combat = helper.start_combat([Cultist()])
    state.drive_actions()
    combat._execute_player_start_phase()
    for pile in player.card_manager.piles.values():
        pile.clear()
    player.powers = []
    player.energy = 3
    player.block = 0
    player.card_manager.piles['draw_pile'] = [Defend() for _ in range(12)]
    return state, player, combat


def assert_finished(state, player):
    assert not state.pending_card_plays
    assert not state.active_card_plays
    assert not player.card_manager.piles['limbo']
    cards = [card for pile in player.card_manager.piles.values() for card in pile]
    assert len(cards) == len({id(card) for card in cards})


@pytest.mark.parametrize('card_class', [Reflex, Tactician])
@pytest.mark.parametrize('upgraded', [False, True])
@pytest.mark.parametrize('via_survivor', [False, True])
def test_manual_discard_rewards_and_completes_play(combat_context, card_class, upgraded, via_survivor):
    state, player, _ = combat_context
    card = card_class()
    if upgraded:
        card.upgrade()
    assert not card.can_play()[0]
    player.card_manager.piles['hand'] = [card]
    if via_survivor:
        survivor = Survivor()
        player.card_manager.piles['hand'].append(survivor)
        state.add_action(PlayCardAction(survivor))
    else:
        state.add_action(DiscardCardAction(card, source_pile='hand'))
    state.drive_actions()
    assert card in player.card_manager.piles['discard_pile']
    assert player.block == (8 if via_survivor else 0)
    assert len(player.card_manager.piles['hand']) == ((3 if upgraded else 2) if card_class is Reflex else 0)
    expected_energy = 3 - int(via_survivor)
    if card_class is Tactician:
        expected_energy += 2 if upgraded else 1
    assert player.energy == expected_energy
    assert_finished(state, player)


@pytest.mark.parametrize('card_class', [Reflex, Tactician])
@pytest.mark.parametrize('upgraded', [False, True])
def test_natural_turn_end_does_not_trigger_manual_reward(combat_context, card_class, upgraded):
    state, player, combat = combat_context
    card = card_class()
    if upgraded:
        card.upgrade()
    player.card_manager.piles['hand'] = [card]
    combat._end_player_phase()
    assert card in player.card_manager.piles['discard_pile']
    assert len(player.card_manager.piles['draw_pile']) == 12
    assert player.energy == 3
    assert_finished(state, player)


@pytest.mark.parametrize('card_class', [Reflex, Tactician])
@pytest.mark.parametrize('upgraded', [False, True])
def test_discarding_other_card_does_not_trigger_reward(combat_context, card_class, upgraded):
    state, player, _ = combat_context
    card = card_class()
    if upgraded:
        card.upgrade()
    other = Defend()
    player.card_manager.piles['hand'] = [card, other]
    state.add_action(DiscardCardAction(other, source_pile='hand'))
    state.drive_actions()
    assert player.card_manager.piles['hand'] == [card]
    assert len(player.card_manager.piles['draw_pile']) == 12
    assert player.energy == 3
    assert_finished(state, player)


@pytest.mark.parametrize('card_class', [Reflex, Tactician])
@pytest.mark.parametrize('upgraded', [False, True])
def test_same_card_triggers_once_per_manual_discard(combat_context, card_class, upgraded):
    state, player, _ = combat_context
    card = card_class()
    if upgraded:
        card.upgrade()
    player.card_manager.piles['hand'] = [card]
    state.add_action(DiscardCardAction(card, source_pile='hand'))
    state.drive_actions()
    # Only one discarded card exists, so a real empty-deck shuffle draws it.
    player.card_manager.piles['draw_pile'].clear()
    state.add_action(DrawCardsAction(count=1))
    state.drive_actions()
    assert card in player.card_manager.piles['hand']
    player.card_manager.piles['draw_pile'] = [Defend() for _ in range(12)]
    state.add_action(DiscardCardAction(card, source_pile='hand'))
    state.drive_actions()
    if card_class is Reflex:
        assert len(player.card_manager.piles['hand']) == 2 * (3 if upgraded else 2)
        assert player.energy == 3
    else:
        assert player.energy == 3 + 2 * (2 if upgraded else 1)
    assert_finished(state, player)


@pytest.mark.parametrize('upgraded', [False, True])
def test_both_discard_cards_keep_their_own_rewards(combat_context, upgraded):
    state, player, _ = combat_context
    reflex, tactician = Reflex(), Tactician()
    if upgraded:
        reflex.upgrade()
        tactician.upgrade()
    player.card_manager.piles['hand'] = [reflex, tactician]
    state.add_action(DiscardCardAction(reflex, source_pile='hand'))
    state.add_action(DiscardCardAction(tactician, source_pile='hand'))
    state.drive_actions()
    assert len(player.card_manager.piles['hand']) == (3 if upgraded else 2)
    assert player.energy == 3 + (2 if upgraded else 1)
    assert_finished(state, player)
