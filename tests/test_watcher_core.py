from enemies.act1.cultist import Cultist
from engine.runtime_api import publish_message
from player.player_factory import create_player
from relics.character.watcher import PureWater, VioletLotus
from tests.test_combat_utils import create_test_helper
from utils.types import StatusType


def test_watcher_factory_builds_starting_deck_and_relic():
    player = create_player("Watcher")

    assert player.max_hp == 72
    assert len(player.card_manager.get_pile("deck")) == 10
    assert any(relic.__class__.__name__ == "PureWater" for relic in player.relics)


def test_pure_water_adds_miracle_on_combat_start():
    helper = create_test_helper()
    player = helper.create_player()
    player.relics = [PureWater()]

    helper.start_combat([helper.create_enemy(Cultist, hp=20)])
    helper.game_state.drive_actions()

    names = [card.__class__.__name__ for card in player.card_manager.get_pile("hand")]
    assert "Miracle" in names


def test_watcher_stance_actions_and_violet_lotus_grant_energy():
    helper = create_test_helper()
    player = helper.create_player(energy=1, max_energy=3)
    player.relics = [VioletLotus()]

    from actions.watcher import ChangeStanceAction

    player.status_manager.status = StatusType.CALM
    ChangeStanceAction(StatusType.WRATH).execute()
    helper.game_state.drive_actions()

    assert player.status_manager.status == StatusType.WRATH
    assert player.energy == 4


def test_flurry_and_weave_return_from_discard_on_triggers():
    helper = create_test_helper()
    player = helper.create_player()

    from cards.watcher import FlurryOfBlows, Weave
    from engine.messages import ScryMessage, StanceChangedMessage

    flurry = FlurryOfBlows()
    weave = Weave()
    helper.add_card_to_discard_pile(flurry)
    helper.add_card_to_discard_pile(weave)

    publish_message(StanceChangedMessage(owner=player, previous_status=StatusType.NEUTRAL, new_status=StatusType.WRATH))
    helper.game_state.drive_actions()
    publish_message(ScryMessage(owner=player, count=1))
    helper.game_state.drive_actions()

    hand_names = [card.__class__.__name__ for card in player.card_manager.get_pile("hand")]
    assert "FlurryOfBlows" in hand_names
    assert "Weave" in hand_names


def test_pressure_points_applies_mark_and_triggers_hp_loss():
    helper = create_test_helper()
    player = helper.create_player()
    enemy = helper.create_enemy(Cultist, hp=30)
    helper.start_combat([enemy])

    from cards.watcher import PressurePoints

    card = PressurePoints()
    helper.add_card_to_hand(card)
    helper.play_card(card, enemy)

    mark = enemy.get_power("Mark")
    assert mark is not None
    assert mark.amount == 8
    assert enemy.hp == 22
