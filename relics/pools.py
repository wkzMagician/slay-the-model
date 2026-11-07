"""Run-owned relic pools using the fixed original registration order."""
from functools import lru_cache
import importlib
import json
from pathlib import Path

from utils.compatible_random import JavaRandom48
from utils.types import RarityType

TIERS = ("COMMON", "UNCOMMON", "RARE", "SHOP", "BOSS")
FALLBACK = {"COMMON": "UNCOMMON", "UNCOMMON": "RARE", "SHOP": "UNCOMMON"}


@lru_cache(maxsize=1)
def catalog():
    return json.loads(Path(__file__).with_name("original_pools.json").read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def definitions():
    return {row["key"]: row for row in catalog()["relics"]}


def make_relic(key):
    row = definitions()[key]
    relic = getattr(importlib.import_module(row["module"]), row["cls"])()
    relic._original_relic_id = row["id"]
    return relic


class RelicPools:
    def __init__(self, child_seeds):
        self.remaining: dict[str, list[str] | None] = {tier: None for tier in TIERS}
        self.rngs = {tier.upper(): JavaRandom48(seed) for tier, seed in child_seeds.items()}

    def initialize(self, tier):
        from engine.game_state import game_state
        by_original = {row["id"]: row["key"] for row in catalog()["relics"]}
        namespace = game_state.player.namespace
        profiles = catalog()["pools"]
        if namespace in profiles:
            ids = profiles[namespace][tier]
        else:
            shared = {row["id"] for row in catalog()["relics"] if row["namespace"] == "any"}
            ids = [value for value in profiles["ironclad"][tier] if value in shared]
        keys = [by_original[value] for value in ids]
        self.rngs[tier].shuffle(keys)
        self.remaining[tier] = keys

    def draw(self, tier, exclude=(), characters=None, *, from_end=False):
        from engine.game_state import game_state
        from relics.global_relics.special import Circlet, RedCirclet

        name = tier.name if isinstance(tier, RarityType) else tier
        allowed = {value.lower() for value in characters} | {"any", "global"} if characters else None
        owned = set(game_state.obtained_relics)
        owned.update(getattr(relic, "idstr", None) for relic in game_state.player.relics)
        blocked = set(exclude) | owned
        use_end = from_end and name != "BOSS"
        while True:
            if self.remaining[name] is None:
                self.initialize(name)
            pool = self.remaining[name]
            assert pool is not None
            if not pool:
                if name in FALLBACK:
                    return self.draw(FALLBACK[name], exclude, characters)
                return RedCirclet() if name == "BOSS" else Circlet()
            key = pool.pop(-1 if use_end else 0)
            relic = make_relic(key)
            original = definitions()[key]["id"]
            valid = key not in blocked and original not in blocked
            valid = valid and (allowed is None or relic.namespace in allowed)
            if valid and relic.can_spawn():
                legacy = getattr(relic, "canSpawn", None)
                if not callable(legacy) or legacy():
                    return relic
            # Original returnRandomRelicKey delegates rejected candidates to
            # returnEndRandomRelicKey; rejected entries have already been removed.
            use_end = name != "BOSS"
