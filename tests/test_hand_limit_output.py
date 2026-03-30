from tests.test_combat_utils import create_test_helper
from actions.card import AddCardAction, DrawCardsAction
from cards.colorless.burn import Burn
from cards.colorless.void import Void
from cards.ironclad.strike import Strike
from utils.types import PilePosType


def _fill_hand(player):
    for _ in range(10):
        player.card_manager.add_to_pile(Strike(), "hand", PilePosType.TOP)


def test_add_card_action_prints_hand_full_redirect(capsys):
    helper = create_test_helper()
    player = helper.create_player(hp=80, max_hp=80, energy=3)
    _fill_hand(player)

    overflow = Burn()
    AddCardAction(card=overflow, dest_pile="hand").execute()

    output = capsys.readouterr().out.lower()
    assert overflow in player.card_manager.get_pile("discard_pile")
    assert "hand" in output
    assert "discard" in output


def test_draw_cards_action_prints_hand_full_redirect(capsys):
    helper = create_test_helper()
    player = helper.create_player(hp=80, max_hp=80, energy=3)
    _fill_hand(player)
    overflow = Void()
    player.card_manager.add_to_pile(overflow, "draw_pile", PilePosType.TOP)

    DrawCardsAction(count=1).execute()
    helper.game_state.drive_actions()

    output = capsys.readouterr().out.lower()
    assert overflow in player.card_manager.get_pile("discard_pile")
    assert overflow not in player.card_manager.get_pile("hand")
    assert "hand" in output
    assert "discard" in output
