from actions.combat import EndTurnAction, PlayCardAction
from cards.ironclad.strike import Strike
from engine.game_state import GameState
from engine.input_protocol import InputRequest
from utils.option import Option


class _DummyCombat:
    pass


def test_debug_selection_prefers_attack_over_end_turn_in_combat():
    gs = GameState()
    gs.current_combat = _DummyCombat()

    request = InputRequest(
        options=[
            Option(name='End', actions=[EndTurnAction()]),
            Option(name='Strike', actions=[PlayCardAction(Strike())]),
        ],
        max_select=1,
    )

    assert gs._resolve_debug_selection(request) == [1]


def test_debug_selection_honors_game_state_score_override():
    gs = GameState()
    gs.current_combat = _DummyCombat()

    seen = []

    def fake_score(option):
        seen.append(str(option.name))
        return 100 if str(option.name) == "End" else 0

    gs._score_debug_option = fake_score

    request = InputRequest(
        options=[
            Option(name="End", actions=[EndTurnAction()]),
            Option(name="Strike", actions=[PlayCardAction(Strike())]),
        ],
        max_select=1,
    )

    assert gs._resolve_debug_selection(request) == [0]
    assert seen == ["End", "Strike"]
