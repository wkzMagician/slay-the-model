"""Fixed role potion pools and the original full-pool rejection protocol."""
from functools import lru_cache
import importlib
import json
from pathlib import Path
from typing import cast

from engine.random_streams import StreamRandom, get_rng


@lru_cache(maxsize=1)
def catalog():
    return json.loads(Path(__file__).with_name("original_pools.json").read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def definitions():
    return {row["id"]: row for row in catalog()["potions"]}


def draw_potion(namespace, rarities=None, *, uniform=False, limited=False):
    rng = cast(StreamRandom, get_rng("potion"))
    ids = catalog()["pools"][namespace]
    rows = definitions()
    if uniform:
        selected = rng.choice(ids)
    else:
        if rarities:
            allowed = {rarity.name for rarity in rarities}
        else:
            roll = rng.random_int(0, 99)
            rarity = "COMMON" if roll < 65 else "UNCOMMON" if roll < 90 else "RARE"
            allowed = {rarity}
        if not any(rows[value]["rarity"] in allowed and (not limited or value != "Fruit Juice") for value in ids):
            return None
        selected = rng.choice(ids)
        reject_limited = limited
        for _ in range(10000):
            if rows[selected]["rarity"] in allowed and not reject_limited:
                break
            selected = rng.choice(ids)
            reject_limited = limited and selected == "Fruit Juice"
        else:
            raise RuntimeError("Potion rejection exceeded its safety limit")
    row = rows[selected]
    potion = getattr(importlib.import_module(row["module"]), row["cls"])()
    potion._original_potion_id = selected
    return potion
