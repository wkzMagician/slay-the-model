"""Run-local event consumption and a dedicated, reproducible random stream."""
import random
from engine.random_streams import StreamRandom


class EventPoolState:
    def __init__(self, seed: int = 0, rng: random.Random | StreamRandom | None = None):
        self.seed = seed
        self.rng = rng if rng is not None else StreamRandom(seed)
        self.current_act = 1
        self.used_in_act: set[str] = set()
        self.used_once: set[str] = set()

    def enter_act(self, act: int) -> None:
        if act != self.current_act:
            self.current_act = act
            self.used_in_act.clear()

    def reset(self, seed: int | None = None) -> None:
        if seed is not None:
            self.seed = seed
        self.rng.seed(self.seed)
        self.current_act = 1
        self.used_in_act.clear()
        self.used_once.clear()
