from actions.combat import GainBlockAction
from engine.messages import EliteVictoryMessage
from engine.message_bus import MessageBus
from engine.subscriptions import MessagePriority, subscribe
from relics.base import Relic
from rooms.combat import CombatRoom
from tests.test_combat_utils import create_test_helper
from utils.types import RoomType


class _EliteVictoryRelic(Relic):
    def __init__(self):
        super().__init__()
        self.triggered = False

    @subscribe(EliteVictoryMessage, priority=MessagePriority.PLAYER_RELIC)
    def on_elite_victory(self):
        from engine.game_state import game_state
        self.triggered = True
        player = game_state.player
        assert player is not None
        return [GainBlockAction(block=8, target=player)]


def test_message_bus_dispatches_elite_victory_subscription():
    helper = create_test_helper()
    player = helper.create_player(hp=80, max_hp=80, energy=3)
    relic = _EliteVictoryRelic()

    actions = MessageBus().publish(
        EliteVictoryMessage(owner=player, room=None, encounter_name="TestElite"),
        participants=[relic],
    )

    assert relic.triggered is True
    assert len(actions) == 1
    assert isinstance(actions[0], GainBlockAction)


def test_combat_room_elite_victory_publishes_elite_victory_message(monkeypatch):
    helper = create_test_helper()
    player = helper.create_player(hp=80, max_hp=80, energy=3)
    relic = _EliteVictoryRelic()
    player.relics = [relic]

    room = CombatRoom(room_type=RoomType.ELITE, encounter_name="TestElite")
    room.enemies = []
    room.init()

    published = []
    original_publish = helper.game_state.publish_message

    def wrapped(message, *args, **kwargs):
        published.append(type(message).__name__)
        return original_publish(message, *args, **kwargs)

    monkeypatch.setattr(helper.game_state, "publish_message", wrapped)

    actions = room._handle_victory()
    for action in actions:
        action.execute()
    helper.game_state.drive_actions()

    assert "EliteVictoryMessage" in published
    assert relic.triggered is True
    assert player.block == 8
