from cards.ironclad.strike import Strike
from events import match_and_keep as mod


def test_match_and_keep_end_game_stringifies_card_info_and_returns_actions():
    event = mod.MatchAndKeepAction()
    mod._matching_state = {'matched_cards': [Strike()]}

    result = event._end_game()

    assert result is not None
    assert mod._matching_state == {}
