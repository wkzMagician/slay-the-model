from actions.card import AddCardAction
from cards.colorless.burn import Burn
from engine.game_state import game_state


def test_add_card_action_accepts_legacy_target_argument():
    discard_pile = game_state.player.card_manager.get_pile("discard_pile")
    discard_pile.clear()

    action = AddCardAction(
        card=Burn(),
        target=game_state.player,
        dest_pile="discard_pile",
        source="enemy",
    )

    result = action.execute()

    assert result is not None
    assert len(discard_pile) == 1
    assert discard_pile[0].__class__.__name__ == "Burn"
