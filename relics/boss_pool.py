"""Run-wide Boss relic draws without replacement."""
from random import Random
from typing import TYPE_CHECKING, Sequence

from utils.registry import get_registered_instance, list_registered
from utils.types import RarityType

if TYPE_CHECKING:
    from relics.base import Relic


class BossRelicPool:
    def __init__(self, seed: int):
        self.remaining: list[str] | None = None
        self.rng = Random(f"{seed}:boss_relics")

    def _initialize(self) -> None:
        import relics  # Register all character and global relics before building the pool.
        from engine.game_state import game_state

        namespace = game_state.player.namespace
        candidates = []
        for relic_id in sorted(list_registered("relic")):
            relic = get_registered_instance("relic", relic_id)
            if relic is not None and relic.rarity == RarityType.BOSS and relic.namespace in ("any", "global", namespace):
                candidates.append(relic_id)
        self.rng.shuffle(candidates)
        self.remaining = candidates

    def draw(self, exclude: Sequence[str] = (), characters: Sequence[str] | None = None) -> "Relic":
        from engine.game_state import game_state
        from relics.global_relics.special import RedCirclet

        if self.remaining is None:
            self._initialize()
        assert self.remaining is not None
        owned = {getattr(relic, "idstr", None) for relic in game_state.player.relics}
        allowed = {name.lower() for name in characters} | {"any", "global"} if characters else None
        while self.remaining:
            relic_id = self.remaining.pop(0)
            if relic_id in exclude or relic_id in owned or relic_id in game_state.obtained_relics:
                continue
            relic = get_registered_instance("relic", relic_id)
            if relic is None or (allowed is not None and relic.namespace not in allowed):
                continue
            if not relic.can_spawn():
                continue
            legacy_can_spawn = getattr(relic, "canSpawn", None)
            if callable(legacy_can_spawn) and not legacy_can_spawn():
                continue
            return relic
        return RedCirclet()


def draw_boss_relic() -> "Relic":
    from engine.game_state import game_state

    return game_state.boss_relic_pool.draw()


def draw_boss_relic_choices(count: int = 3) -> list["Relic"]:
    return [draw_boss_relic() for _ in range(count)]
