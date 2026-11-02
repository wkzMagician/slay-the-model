from __future__ import annotations
from engine.random_streams import get_rng, StreamRandom

from typing import Any

from typing import cast

from engine.game_flow import GameFlow
from engine.game_state import GameState
from actions.display import InputRequestAction
from events.base_event import Event
from events.dead_adventurer import DeadAdventurer
from events.hypnotizing_mushrooms import HypnotizingColoredMushrooms
from events.the_mausoleum import TheMausoleum
from events.event_pool import EventPool
from rooms.event import EventRoom
from rooms.rest import RestRoom
from tests.test_combat_utils import create_test_helper
from utils.types import RarityType, RoomType


def test_event_pool_respects_event_class_can_appear():
    class NeverEvent(Event):
        @classmethod
        def can_appear(cls) -> bool:
            return False

    pool = EventPool()
    pool.register_event(NeverEvent, event_id="never_event", acts=[1])

    assert pool.get_available_events(1) == []


def test_get_random_events_removes_selected_event_for_the_run(monkeypatch):
    import importlib

    from utils.random import get_random_events
    event_pool_module = importlib.import_module("events.event_pool")

    class OnceEvent(Event):
        pass

    pool = EventPool()
    pool.register_event(OnceEvent, event_id="once_event", acts=[1])
    monkeypatch.setattr(event_pool_module, "event_pool", pool)

    first = get_random_events(act=1, count=1)
    second = get_random_events(act=1, count=1)

    assert len(first) == 1
    assert isinstance(first[0], OnceEvent)
    assert second == []


def test_get_random_relic_defaults_to_current_character(monkeypatch):
    from utils.random import get_random_relic

    helper = create_test_helper()
    player = helper.create_player()
    player.namespace = "ironclad"
    helper.game_state.obtained_relics = set()

    class _BaseRelic:
        rarity = RarityType.COMMON

        def can_spawn(self) -> bool:
            return True

    class SilentRelic(_BaseRelic):
        namespace = "silent"

    class IroncladRelic(_BaseRelic):
        namespace = "ironclad"

    class AnyRelic(_BaseRelic):
        namespace = "any"

    registry = {
        "SilentRelic": SilentRelic,
        "IroncladRelic": IroncladRelic,
        "AnyRelic": AnyRelic,
    }

    monkeypatch.setattr("utils.random.list_registered", lambda kind: list(registry) if kind == "relic" else [])
    monkeypatch.setattr("utils.random.get_registered", lambda kind, name: registry.get(name) if kind == "relic" else None)
    monkeypatch.setattr(get_rng("relic"), "choice", lambda seq: seq[0])

    relic = get_random_relic()

    assert relic is not None
    assert relic.namespace != "silent"


def test_get_random_potion_rolls_rarity_before_sampling(monkeypatch):
    from utils.random import get_random_potion

    helper = create_test_helper()
    player = helper.create_player()
    player.character = "IRONCLAD"

    class CommonPotion:
        rarity = RarityType.COMMON
        category = "ironclad"

    class UncommonPotion:
        rarity = RarityType.UNCOMMON
        category = "ironclad"

    class RarePotion:
        rarity = RarityType.RARE
        category = "ironclad"

    registry = {
        "CommonPotion": CommonPotion,
        "UncommonPotion": UncommonPotion,
        "RarePotion": RarePotion,
    }

    monkeypatch.setattr("utils.random.list_registered", lambda kind: list(registry) if kind == "potion" else [])
    monkeypatch.setattr("utils.random.get_registered", lambda kind, name: registry.get(name) if kind == "potion" else None)
    monkeypatch.setattr(get_rng("potion"), "random", lambda: 0.8)
    monkeypatch.setattr(get_rng("potion"), "choice", lambda seq: seq[0])

    potion = get_random_potion()

    assert potion is not None
    assert potion.rarity == RarityType.UNCOMMON


def test_event_room_stays_until_event_ends():
    room = EventRoom()

    class DummyEvent:
        event_ended = False

        def trigger(self):
            return None

    event = DummyEvent()
    room._trigger_event(event)

    assert room.triggered_event is event
    assert room.should_leave is False


def test_game_flow_does_not_leave_room_until_should_leave_is_true():
    gs = GameState()
    flow = GameFlow()

    class DummyRoom:
        should_leave = False

        def __init__(self):
            self.init_calls = 0
            self.enter_calls = 0
            self.leave_calls = 0

        def init(self):
            self.init_calls += 1

        def enter(self):
            self.enter_calls += 1
            return None

        def leave(self):
            self.leave_calls += 1

    room = DummyRoom()
    flow.current_room = room
    flow.flow_phase = "enter_room"

    flow._execute_enter_room_phase(gs)

    assert room.init_calls == 1
    assert room.enter_calls == 1
    assert room.leave_calls == 0
    assert flow.current_room is room
    assert flow.flow_phase == "enter_room"

    room.should_leave = True
    flow._execute_enter_room_phase(gs)

    assert room.init_calls == 1
    assert room.enter_calls == 1
    assert room.leave_calls == 1
    assert flow.current_room is None
    assert flow.flow_phase == "select_room"


def test_rest_room_runs_generic_relic_enter_hook():
    helper = create_test_helper()
    helper.create_player()

    called: dict[str, Any] = {"value": False}

    class DummyRelic:
        def onEnterRestRoom(self):
            called["value"] = True

    helper.game_state.player.relics = [DummyRelic()]

    room = RestRoom()
    room.enter()

    assert called["value"] is True


def test_act4_map_uses_five_room_sequence():
    from map.map_manager import MapManager

    manager = MapManager(seed=7, act_id=4)
    map_data = manager.generate_map()

    assert map_data.floor_count == 5
    assert [floor[0].room_type for floor in map_data.nodes] == [
        RoomType.REST,
        RoomType.MERCHANT,
        RoomType.ELITE,
        RoomType.BOSS,
        RoomType.VICTORY,
    ]


def test_juzu_bracelet_keeps_monster_counter_reset_when_monster_roll_is_redirected():
    from map.map_manager import MapManager

    manager = MapManager(seed=11, act_id=1)
    manager.set_relic_effect("juzu_bracelet", True)
    manager.unknown_room_visits[RoomType.MONSTER] = 3

    original_randint = manager.random_streams["event"].randint
    manager.random_streams["event"].randint = lambda a, b: 1
    try:
        result = manager._resolve_unknown_type(7)
    finally:
        manager.random_streams["event"].randint = original_randint

    assert result == RoomType.EVENT
    assert manager.unknown_room_visits[RoomType.MONSTER] == 0


def test_dead_adventurer_search_without_elite_rebuilds_event_menu(monkeypatch):
    helper = create_test_helper()
    helper.create_player()
    helper.game_state.floor_in_act = 11
    helper.game_state.ascension = 0
    helper.game_state.action_queue.clear()

    event = DeadAdventurer()

    monkeypatch.setattr(get_rng("misc"), "randint", lambda a, b: 100)
    monkeypatch.setattr(get_rng("misc"), "choice", lambda seq: seq[0])

    event.trigger()

    menu = cast(InputRequestAction, helper.game_state.action_queue.queue[-1])
    assert isinstance(menu, InputRequestAction)

    for action in menu.options[0].actions:
        action.execute()

    assert any(isinstance(action, InputRequestAction) for action in helper.game_state.action_queue.queue)


def test_event_end_marks_current_event_room_for_leave():
    helper = create_test_helper()
    helper.create_player()

    room = EventRoom()
    event = Event()
    room.triggered_event = event
    helper.game_state.current_room = room

    event.end_event()

    assert event.event_ended is True
    assert room.should_leave is True


def test_the_mausoleum_option_ends_event():
    helper = create_test_helper()
    helper.create_player()
    helper.game_state.action_queue.clear()

    event = TheMausoleum()
    event.trigger()

    menu = cast(InputRequestAction, helper.game_state.action_queue.queue[-1])
    assert isinstance(menu, InputRequestAction)

    for action in menu.options[0].actions:
        action.execute()

    assert event.event_ended is True


def test_hypnotizing_mushrooms_option_ends_event():
    helper = create_test_helper()
    helper.create_player()
    helper.game_state.floor_in_act = 11
    helper.game_state.action_queue.clear()

    event = HypnotizingColoredMushrooms()
    event.trigger()

    menu = cast(InputRequestAction, helper.game_state.action_queue.queue[-1])
    assert isinstance(menu, InputRequestAction)

    for action in menu.options[1].actions:
        action.execute()

    assert event.event_ended is True


def test_hypnotizing_mushrooms_option_text_describes_effects():
    helper = create_test_helper()
    helper.create_player()
    helper.game_state.floor_in_act = 11
    helper.game_state.action_queue.clear()

    event = HypnotizingColoredMushrooms()
    event.trigger()

    menu = cast(InputRequestAction, helper.game_state.action_queue.queue[-1])
    assert isinstance(menu, InputRequestAction)

    option_details = [str(getattr(option, "detail", "")) for option in menu.options]

    assert any("Odd Mushroom" in text for text in option_details)
    assert any("25%" in text and "Parasite" in text for text in option_details)


def test_we_meet_again_option_text_describes_trade_effects(monkeypatch):
    from events.we_meet_again import WeMeetAgain
    from cards.ironclad.inflame import Inflame
    from potions.global_potions import FruitJuice

    def offer(kind: str) -> list[str]:
        helper = create_test_helper()
        player = helper.create_player()
        player.gold = 100
        player.potions.append(FruitJuice())
        player.card_manager.deck.append(Inflame())
        helper.game_state.action_queue.clear()
        monkeypatch.setattr(
            get_rng("misc"), "choice",
            lambda seq: kind if kind in seq else seq[0],
        )
        monkeypatch.setattr(get_rng("misc"), "randint", lambda a, b: 50)
        WeMeetAgain().trigger()
        menu = cast(InputRequestAction, helper.game_state.action_queue.queue[-1])
        assert isinstance(menu, InputRequestAction)
        return [str(option.name) for option in menu.options]

    potion_texts = offer("potion")
    assert any("random relic" in text.lower() and "potion" in text.lower() for text in potion_texts)

    gold_texts = offer("gold")
    assert any("gold" in text.lower() and "random relic" in text.lower() for text in gold_texts)

    card_texts = offer("card")
    assert any("remove" in text.lower() and "random relic" in text.lower() for text in card_texts)
