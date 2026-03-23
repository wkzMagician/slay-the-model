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
