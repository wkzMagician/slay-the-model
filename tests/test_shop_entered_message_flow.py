from actions.combat import GainBlockAction
from engine.messages import ShopEnteredMessage
from engine.message_bus import MessageBus
from engine.subscriptions import MessagePriority, subscribe
from relics.base import Relic
from rooms.shop import ShopRoom
from tests.test_combat_utils import create_test_helper
from utils.result_types import MultipleActionsResult, SingleActionResult


def _execute_result(result):
    if result is None:
        return

    if isinstance(result, SingleActionResult):
        _execute_result(result.action.execute())
        return

    if isinstance(result, MultipleActionsResult):
        for action in result.actions:
            _execute_result(action.execute())
        return

    if hasattr(result, "execute"):
        _execute_result(result.execute())


class _ShopEnterRelic(Relic):
    def __init__(self):
        super().__init__()
        self.triggered = False

    @subscribe(ShopEnteredMessage, priority=MessagePriority.PLAYER_RELIC)
    def on_shop_enter(self, player, entities=None):
        self.triggered = True
        return [GainBlockAction(block=6, target=player)]


def test_message_bus_dispatches_shop_entered_subscription():
    helper = create_test_helper()
    player = helper.create_player(hp=80, max_hp=80, energy=3)
    relic = _ShopEnterRelic()

    actions = MessageBus().publish(
        ShopEnteredMessage(owner=player, room=None),
        participants=[relic],
    )

    assert relic.triggered is True
    assert len(actions) == 1
    assert isinstance(actions[0], GainBlockAction)


def test_shop_room_enter_publishes_shop_entered_message(monkeypatch):
    helper = create_test_helper()
    player = helper.create_player(hp=80, max_hp=80, energy=3)
    relic = _ShopEnterRelic()
    player.relics = [relic]
    room = ShopRoom()
    room.init()

    published = []
    original_publish = helper.game_state.publish_message

    def wrapped(message, *args, **kwargs):
        published.append(type(message).__name__)
        return original_publish(message, *args, **kwargs)

    monkeypatch.setattr(helper.game_state, "publish_message", wrapped)

    result = room.enter()
    assert isinstance(result, MultipleActionsResult)
    assert result.actions
    assert isinstance(result.actions[0], GainBlockAction)
    assert any(action.__class__.__name__ == "InputRequestAction" for action in result.actions)

    _execute_result(result)
    helper.game_state.drive_actions()

    assert "ShopEnteredMessage" in published
    assert relic.triggered is True
    assert player.block == 6
