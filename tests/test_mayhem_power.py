from cards.ironclad.strike import Strike
from engine.game_state import game_state
from powers.definitions.mayhem import MayhemPower
from utils.types import PilePosType


def test_mayhem_power_uses_draw_pile_on_turn_start():
    card_manager = game_state.player.card_manager
    card_manager.get_pile("draw_pile").clear()
    card_manager.get_pile("hand").clear()
    top_card = Strike()
    card_manager.add_to_pile(top_card, "draw_pile", pos=PilePosType.TOP)

    power = MayhemPower(owner=game_state.player)

    actions = power.on_turn_start()

    assert len(actions) == 1
    assert actions[0].card is top_card
