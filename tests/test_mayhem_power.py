from cards.ironclad.strike import Strike
from enemies.act1.cultist import Cultist
from cards.defect.zap import Zap
from engine.game_state import game_state
from powers.definitions.mayhem import MayhemPower
from tests.test_combat_utils import create_test_helper
from utils.types import PilePosType


def test_mayhem_power_uses_draw_pile_on_turn_start():
    helper = create_test_helper()
    player = helper.create_player()
    player.base_draw_count = 0
    helper.start_combat([Cultist()])
    card_manager = player.card_manager
    card_manager.get_pile("draw_pile").clear()
    card_manager.get_pile("hand").clear()
    top_card = Strike()
    card_manager.add_to_pile(top_card, "draw_pile", pos=PilePosType.TOP)

    power = MayhemPower(owner=game_state.player)

    game_state.action_queue.clear()
    power.on_turn_start()

    assert game_state.drive_actions() is None
    assert card_manager.get_card_location(top_card) == "discard_pile"
    assert top_card not in card_manager.get_pile("hand")


def test_mayhem_plays_top_card_before_normal_turn_draw():
    helper = create_test_helper()
    player = helper.create_player()
    player.base_draw_count = 1
    combat = helper.start_combat([])

    card_manager = player.card_manager
    card_manager.get_pile("draw_pile").clear()
    card_manager.get_pile("hand").clear()

    drawn_after_mayhem = Strike()
    played_by_mayhem = Zap()
    card_manager.add_to_pile(drawn_after_mayhem, "draw_pile", PilePosType.TOP)
    card_manager.add_to_pile(played_by_mayhem, "draw_pile", PilePosType.TOP)

    player.add_power(MayhemPower(owner=player))

    combat._start_player_turn()
    helper.game_state.drive_actions()

    hand = card_manager.get_pile("hand")
    assert drawn_after_mayhem in hand
    assert played_by_mayhem not in hand
    assert len(player.orb_manager.orbs) == 1
