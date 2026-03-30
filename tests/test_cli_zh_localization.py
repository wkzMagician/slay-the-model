import localization

from actions.map_selection import MoveToMapNodeAction, SelectMapNodeAction
from cards.ironclad.bash import Bash
from engine.game_state import game_state
from map.map_manager import MapManager
from map.map_node import MapNode
from powers.definitions.time_warp import TimeWarpPower
from utils.types import RoomType


def setup_function():
    localization.set_language("zh")
    game_state.config.language = "zh"


def teardown_function():
    localization.set_language("en")
    game_state.config.language = "en"


def test_map_text_is_localized_in_zh():
    manager = MapManager(seed=1, act_id=1)
    manager.map_data.nodes = [
        [MapNode(0, 0, RoomType.NEO, connections_up=[0])],
        [MapNode(1, 0, RoomType.MONSTER)],
    ]
    game_state.map_manager = manager
    game_state.current_act = 1
    game_state.current_floor = 0
    manager.map_data.set_current_position(0, 0)

    text = manager.get_map_text_for_human()

    assert "[M]=怪物" in text
    assert "节点上方为索引" in text
    assert "Indices are above nodes" not in text
    assert "Monster" not in text


def test_map_move_option_and_room_entered_use_localized_room_type(capsys):
    manager = MapManager(seed=1, act_id=1)
    manager.map_data.nodes = [
        [MapNode(0, 0, RoomType.NEO, connections_up=[0])],
        [MapNode(1, 0, RoomType.MONSTER)],
    ]
    game_state.map_manager = manager
    game_state.current_act = 1
    game_state.current_floor = 0
    manager.map_data.set_current_position(0, 0)

    option_name = SelectMapNodeAction()._get_move_option_name(manager.map_data.nodes[1][0]).resolve()
    assert "Monster" not in option_name
    assert "怪物" in option_name

    MoveToMapNodeAction(floor=1, position=0).execute()
    output = capsys.readouterr().out
    assert "Monster" not in output
    assert "怪物" in output


def test_card_info_uses_localized_labels_and_values():
    info = str(Bash().info())

    assert "费用" in info
    assert "类型: 攻击" in info
    assert "稀有度: 初始" in info
    assert "Cost:" not in info
    assert "Type:" not in info
    assert "Rarity:" not in info


def test_secret_portal_and_victory_text_have_zh_translations():
    assert localization.t("events.secret_portal.description") != "events.secret_portal.description"
    assert "传送门" in localization.t("events.secret_portal.description")
    assert "尖塔" in localization.t("ui.act3_victory_message")
    assert "钥匙" in localization.t("ui.keys_hint")


def test_time_warp_prints_localized_counter(capsys):
    power = TimeWarpPower(amount=0)

    power.on_card_play(card=None, player=None, targets=[])
    output = capsys.readouterr().out

    assert "Time Warp:" not in output
    assert "时间扭曲" in output
