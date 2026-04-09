from actions.combat import GainBlockAction
from engine.messages import HealedMessage, ShopEnteredMessage
from engine.subscriptions import MessagePriority, subscribe
from relics.base import Relic
from rooms.shop import ShopRoom
from tests.test_combat_utils import create_test_helper


class _HealingRelic(Relic):
    @subscribe(HealedMessage, priority=MessagePriority.PLAYER_RELIC)
    def on_healed(self, amount, source):
        from engine.game_state import game_state
        player = game_state.player
        assert player is not None
        return [GainBlockAction(block=amount, target=player)]


class _ShopRelic(Relic):
    @subscribe(ShopEnteredMessage, priority=MessagePriority.PLAYER_RELIC)
    def on_shop_enter(self):
        from engine.game_state import game_state
        player = game_state.player
        assert player is not None
        return [GainBlockAction(block=6, target=player)]


def test_publish_message_queues_follow_up_actions_in_global_queue():
    helper = create_test_helper()
    player = helper.create_player(hp=35, max_hp=80, energy=3)
    player.relics = [_HealingRelic()]

    result = helper.game_state.publish_message(
        HealedMessage(target=player, amount=10, previous_hp=35, new_hp=45),
    )

    assert result is None
    queued_action = helper.game_state.action_queue.peek_next()
    assert isinstance(queued_action, GainBlockAction)

    helper.game_state.drive_actions()

    assert player.block == 10


def test_shop_room_enter_publishes_without_participants_and_returns_only_menu(monkeypatch):
    helper = create_test_helper()
    player = helper.create_player(hp=80, max_hp=80, energy=3)
    player.relics = [_ShopRelic()]
    room = ShopRoom()
    room.init()

    publish_calls = []
    original_publish = helper.game_state.publish_message

    def wrapped(message, *args, **kwargs):
        publish_calls.append((message, kwargs))
        return original_publish(message, *args, **kwargs)

    monkeypatch.setattr(helper.game_state, "publish_message", wrapped)

    result = room.enter()

    assert result is None
    queued = list(helper.game_state.action_queue.queue)
    assert queued
    assert any(isinstance(action, GainBlockAction) for action in queued)
    assert any(action.__class__.__name__ == "InputRequestAction" for action in queued)
    assert len(publish_calls) == 1
    assert isinstance(publish_calls[0][0], ShopEnteredMessage)
    assert "participants" not in publish_calls[0][1]

    helper.game_state.drive_actions()

    assert player.block == 6
