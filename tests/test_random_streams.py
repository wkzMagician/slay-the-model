"""Native isolation/lifecycle checks and original utility-backed state contracts."""
import json
import random
from types import SimpleNamespace

import pytest

from config.game_config import GameConfig
from engine.game_state import game_state
from engine.random_streams import DOMAINS, ROOM_DOMAINS, RandomStreams, StreamRandom, using_streams
from utils.compatible_random import GameRandom, JavaRandom48
from utils.seed import signed64


def fresh(monkeypatch, seed):
    monkeypatch.setattr(GameConfig, "load", staticmethod(lambda _: GameConfig(seed=seed)))
    game_state.__init__()
    return game_state


def gameplay(streams):
    return {name: streams[name].export_state() for name in DOMAINS}


@pytest.mark.parametrize("seed", [0, 1, 20261029, -2, -(1 << 63), (1 << 63) - 1])
def test_original_initial_domains_and_room_reset(seed):
    streams = RandomStreams(seed)
    expected = GameRandom(seed).export_state()
    assert all(streams[name].export_state() == expected for name in DOMAINS)
    for name in DOMAINS:
        streams[name].random_long()
    persistent = {name: streams[name].export_state() for name in DOMAINS if name not in ROOM_DOMAINS}
    streams.enter_room(19)
    assert all(streams[name].export_state() == GameRandom(signed64(seed + 19)).export_state() for name in ROOM_DOMAINS)
    assert all(streams[name].export_state() == state for name, state in persistent.items())


@pytest.mark.parametrize("act,offset", [(1, 1), (2, 200), (3, 600), (4, 1200)])
def test_native_map_uses_original_chapter_seed(monkeypatch, act, offset):
    state = fresh(monkeypatch, 20261029)
    state.current_act = act
    state.initialize_map()
    assert state.map_manager.seed == 20261029 + offset
    assert state.map_manager.rng is state.random_streams.map_rng
    assert state.map_manager.encounter_pool.rng is state.random_streams["monster"]


@pytest.mark.parametrize("counter,target", [(0, 0), (1, 250), (249, 250), (250, 250), (251, 500), (500, 500), (749, 750), (750, 750), (751, 751)])
def test_card_rng_transition_alignment(counter, target):
    streams = RandomStreams(1)
    streams.enter_act(1)
    streams["card"].set_counter(counter)
    expected = GameRandom(1, counter)
    expected.set_counter(target)
    streams.enter_act(2)
    assert streams["card"].export_state() == expected.export_state()
    streams.enter_act(2)  # Re-querying a map is not another act transition.
    assert streams["card"].export_state() == expected.export_state()


@pytest.mark.parametrize("seed", range(10))
@pytest.mark.parametrize("extra,target", [("card", "relic"), ("potion", "card"), ("relic", "potion"), ("card", "hp"), ("potion", "ai")])
def test_native_generators_do_not_cross_domains(monkeypatch, seed, extra, target):
    from utils.random import get_random_card, get_random_relic, get_random_potion
    from enemies.act1.looter import Looter
    sources = {"card": lambda: get_random_card(namespaces=["ironclad"]),
               "potion": get_random_potion, "relic": get_random_relic}
    def draw_target():
        if target in sources:
            value = sources[target]()
            return getattr(value, "idstr", None)
        if target == "hp":
            return Looter().hp
        enemy = Looter()
        enemy._turn_count = 2
        return enemy.determine_next_intention().name
    first = fresh(monkeypatch, seed)
    expected = draw_target()
    expected_state = gameplay(first.random_streams)
    second = fresh(monkeypatch, seed)
    global_before = random.getstate()
    sources[extra]()
    assert draw_target() == expected
    target_domain = {"card": "card_random", "relic": "relic", "potion": "potion", "hp": "monster_hp", "ai": "ai"}[target]
    assert second.random_streams[target_domain].export_state() == expected_state[target_domain]
    assert random.getstate() == global_before


@pytest.mark.parametrize("factory", ["_create_louse_pair", "_create_triple_louse", "_create_small_slimes", "_create_large_slime", "_create_swarm_slimes", "_create_gremlin_gang", "_create_exordium_thugs", "_create_exordium_wildlife", "_create_three_shapes", "_create_four_shapes", "_create_spheric_guardian_two_shapes"])
def test_variant_factories_are_reproducible_without_system_entropy(factory):
    import map.encounter_pool as module
    def run():
        streams = RandomStreams(20261029)
        streams.enter_room(12)
        with using_streams(streams):
            enemies = getattr(module, factory)()
        return [(type(enemy).__name__, enemy.hp) for enemy in enemies], gameplay(streams)
    expected = run()
    assert all(run() == expected for _ in range(4))


def test_move_resets_before_native_room_construction_and_invalid_move_is_inert(monkeypatch):
    state = fresh(monkeypatch, 20261029)
    state.initialize_map()
    manager = state.map_manager
    before = state.random_streams.export_state()
    with pytest.raises(ValueError):
        manager.move_to_node(999, 999)
    assert state.random_streams.export_state() == before
    node = manager.get_available_moves()[0]
    seen = []
    original = manager._create_room_instance
    def observe(*args, **kwargs):
        seen.append((state.current_floor, state.random_streams.floor, gameplay(state.random_streams)))
        return original(*args, **kwargs)
    monkeypatch.setattr(manager, "_create_room_instance", observe)
    manager.move_to_node(node.floor, node.position)
    floor, stream_floor, states = seen[0]
    assert floor == stream_floor == node.floor
    assert all(states[name] == GameRandom(signed64(state.config.seed + node.floor)).export_state() for name in ROOM_DOMAINS)


def test_boss_pool_uses_fifth_original_long_without_lazy_parent_draws(monkeypatch):
    state = fresh(monkeypatch, 0)
    oracle = GameRandom(0)
    seeds = [oracle.random_long() for _ in range(5)]
    assert list(state.random_streams.relic_pool_seeds.values()) == seeds
    assert state.random_streams["relic"].export_state() == oracle.export_state()
    child = JavaRandom48(seeds[-1])
    assert state.boss_relic_pool.rng.state == child.state
    before = state.random_streams["relic"].export_state()
    state.boss_relic_pool._initialize()
    assert state.random_streams["relic"].export_state() == before


@pytest.mark.parametrize("display_count", [1, 2, 5])
def test_console_and_tui_display_leave_gameplay_unchanged(monkeypatch, display_count):
    from engine.combat import Combat
    from enemies.act1.looter import Looter
    from tui.handlers.display_handler import DisplayHandler
    state = fresh(monkeypatch, 0)
    state.player.card_manager.piles["draw_pile"] = list(state.player.deck[:3])
    original_pile = list(state.player.card_manager.piles["draw_pile"])
    combat = Combat(enemies=[Looter()])
    rendered = []
    handler = DisplayHandler(SimpleNamespace(update_display_content=rendered.append,
                                             update_player_info=lambda *_: None))
    before = gameplay(state.random_streams)
    global_before = random.getstate()
    for _ in range(display_count):
        combat._print_combat_state()
        handler.display_combat(combat, state)
    assert rendered
    assert gameplay(state.random_streams) == before
    assert random.getstate() == global_before
    assert state.player.card_manager.piles["draw_pile"] == original_pile


def test_debug_strategy_uses_only_policy_state(monkeypatch):
    from engine.input_protocol import InputRequest
    from utils.option import Option
    state = fresh(monkeypatch, 42)
    state.config.debug["select_type"] = "random"
    request = InputRequest(options=[Option(str(i), []) for i in range(10)])
    before = gameplay(state.random_streams)
    policy_before = state.random_streams.policy_rng.getstate()
    state.runtime_context.default_resolve_debug_selection(request)
    assert gameplay(state.random_streams) == before
    assert state.random_streams.policy_rng.getstate() != policy_before


@pytest.mark.parametrize("blocked", [False, True])
def test_fixed_gold_is_deterministic_and_does_not_sample(monkeypatch, blocked):
    from actions.reward import AddGoldAction
    from relics.global_relics.boss import Ectoplasm
    state = fresh(monkeypatch, 1)
    state.player.relics = [Ectoplasm()] if blocked else []
    before = gameplay(state.random_streams)
    gold = state.player.gold
    AddGoldAction(10).execute()
    assert state.player.gold == gold + (0 if blocked else 10)
    assert gameplay(state.random_streams) == before


def test_json_random_state_roundtrip_keeps_all_suffixes_and_non_gameplay_states():
    streams = RandomStreams(-2)
    streams.enter_act(2)
    streams.enter_room(25)
    streams.initialize_relic_pool_seeds()
    for name in DOMAINS:
        streams[name].random_int(99)
    streams.display_rng.random()
    streams.policy_rng.random()
    restored = RandomStreams.from_state(json.loads(json.dumps(streams.export_state())))
    assert restored.export_state() == streams.export_state()
    for name in DOMAINS:
        assert [streams[name].random_long() for _ in range(8)] == [restored[name].random_long() for _ in range(8)]
    assert streams.display_rng.random() == restored.display_rng.random()
    assert streams.policy_rng.random() == restored.policy_rng.random()
    # Restoring random state alone is deliberately not a save-game acceptance.


def test_non_gameplay_context_uses_its_own_run_not_the_global_singleton():
    from engine.runtime_context import RuntimeContext
    from engine.input_protocol import InputRequest
    from utils.option import Option
    owner = SimpleNamespace(random_streams=RandomStreams(23),
                            config=GameConfig(debug={"select_type": "random"}))
    context = RuntimeContext(game_state=owner)
    before = game_state.random_streams.export_state()
    own_before = owner.random_streams.policy_rng.getstate()
    context.default_resolve_debug_selection(InputRequest(options=[Option(str(i), []) for i in range(10)]))
    assert game_state.random_streams.export_state() == before
    assert owner.random_streams.policy_rng.getstate() != own_before


def test_incomplete_or_unknown_random_snapshot_is_rejected():
    state = RandomStreams(42).export_state()
    state["version"] = 99
    with pytest.raises(ValueError):
        RandomStreams.from_state(state)
    state["version"] = 1
    del state["streams"]["misc"]
    with pytest.raises(ValueError):
        RandomStreams.from_state(state)


def test_shop_generation_routes_prices_and_nested_card_helpers_separately(monkeypatch):
    from rooms.shop_state import generate_shop_items
    state = fresh(monkeypatch, 42)
    before = gameplay(state.random_streams)
    items = generate_shop_items(player=state.player)
    assert items
    after = gameplay(state.random_streams)
    assert after["merchant"] != before["merchant"]
    assert after["card"] != before["card"]
    assert after["potion"] != before["potion"]
    assert after["card_random"] == before["card_random"]
    assert after["ai"] == before["ai"]


def test_probabilistic_gold_keeps_an_explicit_misc_draw(monkeypatch):
    from actions.reward import AddGoldAction
    state = fresh(monkeypatch, 1)
    before = gameplay(state.random_streams)
    expected = GameRandom.from_state(before["misc"])
    roll = expected.random_float()
    gold = state.player.gold
    AddGoldAction(10, chance=0.25).execute()
    after = gameplay(state.random_streams)
    assert after["misc"] == expected.export_state()
    assert state.player.gold == gold + (10 if roll < 0.25 else 0)
    assert all(after[name] == before[name] for name in DOMAINS if name != "misc")


def test_stasis_card_selection_uses_card_random_not_misc(monkeypatch):
    from enemies.act2.bronze_orb import BronzeOrb
    from enemies.act2.bronze_orb_intentions import Steal
    state = fresh(monkeypatch, 42)
    state.player.card_manager.piles["draw_pile"] = list(state.player.deck)
    orb = BronzeOrb()
    before = gameplay(state.random_streams)
    Steal(orb).execute()
    after = gameplay(state.random_streams)
    assert len(orb.stolen_cards) == 1
    assert after["card_random"]["counter"] == int(before["card_random"]["counter"]) + 1
    assert all(after[name] == before[name] for name in DOMAINS if name != "card_random")
