import pytest

from rooms.combat import CombatRoom
from rooms.event import EventRoom
from rooms.rest import RestRoom
from rooms.shop import ShopRoom
from rooms.treasure import TreasureRoom


@pytest.mark.parametrize(
    "room_factory",
    [
        lambda: CombatRoom(enemies=[], room_type="MONSTER", encounter_name="test"),
        lambda: EventRoom(),
        lambda: RestRoom(),
        lambda: ShopRoom(),
        lambda: TreasureRoom(),
    ],
)
def test_room_does_not_keep_independent_action_queue(room_factory):
    room = room_factory()
    assert not hasattr(room, "action_queue")
