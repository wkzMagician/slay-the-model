from actions.combat import GainBlockAction
from engine.messages import ShopEnteredMessage
from engine.message_bus import MessageBus
from engine.subscriptions import MessagePriority, subscribe
from relics.base import Relic
from rooms.shop import ShopRoom
from tests.test_combat_utils import create_test_helper


class _ShopEnterRelic(Relic):
    def __init__(self):
        super().__init__()
        self.triggered = False

    @subscribe(ShopEnteredMessage, priority=MessagePriority.PLAYER_RELIC)
    def on_shop_enter(self):
        from engine.game_state import game_state
        self.triggered = True
        player = game_state.player
        assert player is not None
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
    assert result is None
    queued = list(helper.game_state.action_queue.queue)
    assert queued
    assert any(isinstance(action, GainBlockAction) for action in queued)
    assert any(action.__class__.__name__ == "InputRequestAction" for action in queued)

    helper.game_state.drive_actions()

    assert "ShopEnteredMessage" in published
    assert relic.triggered is True
    assert player.block == 6
