"""Prepared histories and independent source order lists through consumers."""
import json
from pathlib import Path
from typing import cast

import pytest

from events.event_pool import EventPool
from map.encounter_pool import EncounterPool
from engine.game_state import game_state
from engine.random_streams import RandomStreams
from utils.types import RoomType

ORDER = json.loads((Path(__file__).parent / "fixtures/original_event_order.json").read_text())


@pytest.mark.parametrize("act", [1, 2, 3])
@pytest.mark.parametrize("count", [0, 1, 2, 3, 4])
@pytest.mark.parametrize("seed", [1, 42, 523])
def test_native_room_factory_uses_chapter_specific_easy_count(monkeypatch, act, count, seed):
    game_state.current_act = act
    game_state.random_streams = RandomStreams(seed)
    game_state.initialize_map()
    game_state.normal_encounters_fought = count
    game_state.encounter_history = []
    pool = game_state.map_manager.encounter_pool
    seen = []
    choose = pool.rng.choices

    def observe(values, **kwargs):
        seen.append(list(values))
        return choose(values, **kwargs)

    monkeypatch.setattr(pool.rng, "choices", observe)
    room = game_state.map_manager._create_room_instance(RoomType.MONSTER, floor_in_act=5)
    from rooms.combat import CombatRoom
    assert isinstance(room, CombatRoom)
    expected = pool.easy_pool if count < (3 if act == 1 else 2) else pool.hard_pool
    assert seen == [list(expected)]
    combat_room = cast(CombatRoom, room)
    assert combat_room.enemies
    assert combat_room.encounter_name in expected


@pytest.mark.parametrize("act,last,excluded", [
    (1, "2 Louse", {"3 Louse"}), (1, "Small Slimes", {"Large Slime", "Swarm of Slimes"}),
    (1, "Looter", {"Exordium Thugs"}),
    (2, "Spheric Guardian", {"Sentry and Spheric Guardian"}),
    (2, "3 Byrds", {"Chosen and Byrds"}),
    (2, "Chosen", {"Chosen and Byrds", "Cultist and Chosen"}),
    (3, "3 Shapes", {"4 Shapes"}),
])
@pytest.mark.parametrize("first", [False, True])
def test_first_strong_exclusions_are_chapter_specific(monkeypatch, act, last, excluded, first):
    pool = EncounterPool(42, act_id=act)
    seen = []
    choose = pool.rng.choices

    def observe(values, **kwargs):
        seen.append(set(values))
        return choose(values, **kwargs)

    monkeypatch.setattr(pool.rng, "choices", observe)
    count = (3 if act == 1 else 2) + (0 if first else 1)
    enemies, name = pool.get_normal_encounter(5, encounter_count=count, encounter_history=[last])
    expected = set(pool.hard_pool) - {last} - (excluded if first else set())
    assert seen == [expected]
    assert name in expected and enemies


@pytest.mark.parametrize("history", [[], ["Looter"], ["Red Slaver", "Large Slime"]])
def test_blue_slaver_real_selection_weight_is_two(monkeypatch, history):
    pool = EncounterPool(42, act_id=1)
    seen = []
    choose = pool.rng.choices

    def observe(values, weights, **kwargs):
        seen.append(dict(zip(values, weights)))
        return choose(values, weights=weights, **kwargs)

    monkeypatch.setattr(pool.rng, "choices", observe)
    pool.get_normal_encounter(10, encounter_count=8, encounter_history=history)
    expected = {"Gang of Gremlins": 1, "Large Slime": 2, "Swarm of Slimes": 1,
                "Exordium Thugs": 1.5, "Exordium Wildlife": 1.5, "Blue Slaver": 2,
                "Red Slaver": 1, "3 Louse": 2, "2 Fungi Beasts": 2, "Looter": 2}
    expected = {key: weight for key, weight in expected.items() if key not in history[-2:]}
    assert seen == [expected]


class DummyEvent:
    pass


@pytest.mark.parametrize("reference", ORDER)
@pytest.mark.parametrize("reverse", [False, True])
def test_source_event_order_survives_registration_filtering_and_removal(reference, reverse):
    act = reference["act"] or 1
    pool = EventPool(seed=42)
    category = {"eventList": "event", "shrineList": "shrine", "specialOneTimeEventList": "special"}[reference["kind"]]
    ids = reference["project_ids"]
    enabled = {key: True for key in ids}
    for key in reversed(ids) if reverse else ids:
        pool.register_event(DummyEvent, key, acts=act, category=category,
                            requires_condition=lambda key=key: enabled[key])
    pool._get_state().enter_act(act)
    assert [m.event_id for m in pool.get_available_events(act)] == ids
    removed = ids[len(ids) // 2]
    pool.mark_event_used(removed)
    enabled[ids[0]] = False
    assert [m.event_id for m in pool.get_available_events(act)] == [key for key in ids if key not in (removed, ids[0])]
    before = pool._get_state().rng.getstate()
    assert pool.get_events_by_act(act) == ids
    assert pool._get_state().rng.getstate() == before


def test_actual_event_draw_receives_original_exordium_candidates(monkeypatch):
    reference = next(r for r in ORDER if r["act"] == 1 and r["kind"] == "eventList")
    pool = EventPool(seed=42)
    for key in reversed(reference["project_ids"]):
        pool.register_event(DummyEvent, key)
    rng = pool._get_state().rng
    choose = rng.choices
    seen = []

    def observe(values, **kwargs):
        seen.append([metadata.event_id for metadata in values])
        return choose(values, **kwargs)

    monkeypatch.setattr(rng, "choices", observe)
    chosen = pool.draw_metadata(1)
    assert seen == [reference["project_ids"]]
    assert chosen is not None
    assert [m.event_id for m in pool.get_available_events(1)] == [key for key in reference["project_ids"] if key != chosen.event_id]
