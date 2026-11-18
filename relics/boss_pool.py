"""Run-wide Boss relic draws without replacement."""
from utils.compatible_random import GameRandom
from typing import TYPE_CHECKING, Sequence

from relics.pools import RelicPools
from utils.types import RarityType

if TYPE_CHECKING:
    from relics.base import Relic


class BossRelicPool:
    def __init__(self, seed: int, child_seed: int | None = None, pools: RelicPools | None = None):
        if child_seed is None:
            parent = GameRandom(seed)
            for _ in range(5):
                child_seed = parent.random_long()
        assert child_seed is not None
        self.pools = pools if pools is not None else RelicPools({"boss": child_seed})
        self.rng = self.pools.rngs["BOSS"]

    @property
    def remaining(self) -> list[str] | None:
        return self.pools.remaining["BOSS"]

    @remaining.setter
    def remaining(self, values: list[str] | None) -> None:
        self.pools.remaining["BOSS"] = values

    def _initialize(self) -> None:
        self.pools.initialize("BOSS")

    def draw(self, exclude: Sequence[str] = (), characters: Sequence[str] | None = None) -> "Relic":
        return self.pools.draw(RarityType.BOSS, exclude, characters)


def draw_boss_relic() -> "Relic":
    from engine.game_state import game_state

    return game_state.boss_relic_pool.draw()


def draw_boss_relic_choices(count: int = 3) -> list["Relic"]:
    return [draw_boss_relic() for _ in range(count)]
