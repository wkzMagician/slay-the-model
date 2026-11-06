"""Run-owned random domains and original normal-mode lifecycle.

Legacy selection adapters preserve caller pools/filters. Their presence does not
prove a consumer's weighting, rejection, or timing matches the original game.
"""
from contextlib import contextmanager
from contextvars import ContextVar
from functools import wraps
import math
import random
from typing import Any, Mapping, Sequence, TypeVar

from utils.compatible_random import GameRandom
from utils.seed import signed64

T = TypeVar("T")
DOMAINS = ("monster", "event", "merchant", "card", "treasure", "relic",
           "monster_hp", "potion", "ai", "shuffle", "card_random", "misc")
ROOM_DOMAINS = ("monster_hp", "ai", "shuffle", "card_random", "misc")
RELIC_POOLS = ("common", "uncommon", "rare", "shop", "boss")
_active: ContextVar[Any] = ContextVar("active_random_streams", default=None)
_routes: ContextVar[dict[str, str]] = ContextVar("random_domain_routes", default={})


class StreamRandom(GameRandom):
    """Explicit convenience operations over the compatible primitives.

    choices/sample retain legacy consumer selection shapes; audited original
    consumers should use their exact integer/float/shuffle protocol instead.
    """
    def random(self) -> float:
        return self.random_float()

    def randint(self, a: int, b: int) -> int:
        return self.random_int(a, b)

    def choice(self, values: Sequence[T]) -> T:
        if not values:
            raise IndexError("Cannot choose from an empty sequence")
        return values[self.random_int(len(values) - 1)]

    def choices(self, values: Sequence[T], weights=None, *, k: int = 1) -> list[T]:
        if not values:
            raise IndexError("Cannot choose from an empty sequence")
        if weights is None:
            return [self.choice(values) for _ in range(k)]
        if len(weights) != len(values):
            raise ValueError("weights and population must have equal lengths")
        total = sum(weights)
        if any(w < 0 or not math.isfinite(w) for w in weights) or total <= 0 or not math.isfinite(total):
            raise ValueError("weights must be finite, nonnegative and have a positive total")
        result = []
        for _ in range(k):
            roll = self.random_float() * total
            running = 0
            for value, weight in zip(values, weights):
                running += weight
                if roll < running:
                    result.append(value)
                    break
        return result

    def sample(self, values: Sequence[T], count: int) -> list[T]:
        """Legacy without-replacement selection; not Java shuffle equivalence."""
        remaining = list(values)
        if not 0 <= count <= len(remaining):
            raise ValueError("Sample larger than population or is negative")
        return [remaining.pop(self.random_int(len(remaining) - 1)) for _ in range(count)]

    def seed(self, seed: int) -> None:
        self.raw.set_seed(seed)
        self.counter = 0

    def getstate(self) -> dict[str, str | int]:
        return self.export_state()

    def setstate(self, state: Mapping[str, str | int]) -> None:
        self.restore_state(state)


class RandomStreams:
    def __init__(self, seed: int):
        self.seed = signed64(seed)
        self.streams = {name: StreamRandom(self.seed) for name in DOMAINS}
        self.floor = 0
        self.act = 0
        self.map_rng = StreamRandom(self.seed)
        self.neow_rng = StreamRandom(self.seed)
        # Non-gameplay states never share a generator with any gameplay domain.
        self.display_rng = random.Random(self.seed)
        self.policy_rng = random.Random(self.seed)
        self.relic_pool_seeds: dict[str, int] = {}

    def __getitem__(self, name: str) -> StreamRandom:
        return self.streams[name]

    def enter_act(self, act: int) -> None:
        if not 1 <= act <= 4:
            raise ValueError("Act must be in 1..4")
        if act != self.act:
            if self.act:
                counter = self["card"].counter
                for lower, upper in ((0, 250), (250, 500), (500, 750)):
                    if lower < counter < upper:
                        self["card"].set_counter(upper)
                        break
            self.act = act
            self.map_rng = StreamRandom(self.map_seed(act))

    def map_seed(self, act: int) -> int:
        if not 1 <= act <= 4:
            raise ValueError("Act must be in 1..4")
        return signed64(self.seed + (1, 200, 600, 1200)[act - 1])

    def enter_room(self, floor: int) -> None:
        self.floor = floor
        for name in ROOM_DOMAINS:
            self.streams[name] = StreamRandom(signed64(self.seed + floor))

    def initialize_relic_pool_seeds(self) -> dict[str, int]:
        if not self.relic_pool_seeds:
            self.relic_pool_seeds = {name: self["relic"].random_long() for name in RELIC_POOLS}
        return dict(self.relic_pool_seeds)

    def export_state(self) -> dict:
        return dict(version=1, seed=str(self.seed), act=self.act, floor=self.floor,
                    streams={name: rng.export_state() for name, rng in self.streams.items()},
                    map=self.map_rng.export_state(), neow=self.neow_rng.export_state(),
                    relic_pool_seeds={name: str(seed) for name, seed in self.relic_pool_seeds.items()},
                    display=self.display_rng.getstate(), policy=self.policy_rng.getstate())

    @classmethod
    def from_state(cls, state: Mapping[str, Any]) -> "RandomStreams":
        if state["version"] != 1 or set(state["streams"]) != set(DOMAINS):
            raise ValueError("Unsupported or incomplete random stream state")
        result = cls(int(state["seed"]))
        result.act, result.floor = int(state["act"]), int(state["floor"])
        for name in DOMAINS:
            result[name].restore_state(state["streams"][name])
        result.map_rng.restore_state(state["map"])
        result.neow_rng.restore_state(state["neow"])
        result.relic_pool_seeds = {name: int(seed) for name, seed in state["relic_pool_seeds"].items()}
        def tuples(value):
            return tuple(tuples(item) for item in value) if isinstance(value, (tuple, list)) else value
        result.display_rng.setstate(tuples(state["display"]))
        result.policy_rng.setstate(tuples(state["policy"]))
        return result


def current_streams() -> RandomStreams:
    active = _active.get()
    if active is not None:
        return active
    from engine.game_state import game_state
    return game_state.random_streams


def get_rng(name: str):
    streams = current_streams()
    name = _routes.get().get(name, name)
    if name == "map":
        return streams.map_rng
    if name == "neow":
        return streams.neow_rng
    if name == "display":
        return streams.display_rng
    if name == "policy":
        return streams.policy_rng
    return streams[name]


@contextmanager
def using_streams(streams: RandomStreams):
    """Bind standalone encounter factories or construction to their owning run."""
    token = _active.set(streams)
    try:
        yield
    finally:
        _active.reset(token)


def route_domains(**routes: str):
    """A producer routes nested shared helpers without changing their test APIs."""
    def decorate(function):
        @wraps(function)
        def routed(*args, **kwargs):
            token = _routes.set({**_routes.get(), **routes})
            try:
                return function(*args, **kwargs)
            finally:
                _routes.reset(token)
        return routed
    return decorate
