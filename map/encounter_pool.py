# -*- coding: utf-8 -*-
"""Encounter pool system for selecting enemies.

Rules of Monster Encounters:
- First 3 encounters (Act 1) or 2 (other acts) = Easy Pool
- Remaining encounters = Hard Pool
- Same encounter cannot appear in next 2 encounters
- Act 1 specific constraints for first Hard Pool
- Elites cannot be same twice in a row
"""

from typing import Dict, List, Tuple, Optional
from utils.types import EnemyType
from utils.registry import register


def _get_enemy_classes():
    from enemies.act1.cultist import Cultist
    from enemies.act1.jaw_worm import JawWorm
    from enemies.act1.louse import RedLouse, GreenLouse
    from enemies.act1.spike_slime import SpikeSlime, SpikeSlimeM
    from enemies.act1.slaver import BlueSlaver
    from enemies.act1.fungi_beast import FungiBeast
    return {
        "Cultist": Cultist, "JawWorm": JawWorm,
        "RedLouse": RedLouse, "GreenLouse": GreenLouse,
        "SpikeSlime": SpikeSlime, "SpikeSlimeM": SpikeSlimeM,
        "BlueSlaver": BlueSlaver, "FungiBeast": FungiBeast,
    }


def _get_elite_classes():
    try:
        from enemies.act1.lagavulin import Lagavulin
        from enemies.act1.gremlin_nob import GremlinNob
        from enemies.act1.sentry import Sentry
        return {"Lagavulin": Lagavulin, "GremlinNob": GremlinNob, "Sentry": Sentry}
    except ImportError:
        return {}


class EncounterPool:
    EASY_ENCOUNTER_COUNTS = {1: 3, 2: 2, 3: 2}

    def __init__(self, seed: int):
        import random
        self.rng = random.Random(seed)
        self.normal_pools = self._build_normal_pools()
        self.elite_pools = self._build_elite_pools()

    def _build_normal_pools(self):
        easy = {
            "Cultist": (["Cultist"], 30),
            "Jaw Worm": (["JawWorm"], 30),
            "2 Louses": (["GreenLouse", "RedLouse"], 20),
            "Small Slimes": (["SpikeSlimeM", "SpikeSlimeM"], 15),
            "Looter": (["BlueSlaver"], 5),  # Fallback: no Looter class
        }
        hard = {
            "Big Slime": (["SpikeSlime"], 25),
            "Slaver and Fungi": (["BlueSlaver", "FungiBeast"], 20),
            "2 Fungi Beasts": (["FungiBeast", "FungiBeast"], 15),
            "3 Louses": (["GreenLouse", "GreenLouse", "RedLouse"], 10),
            "Lots of Slimes": (["SpikeSlimeM", "SpikeSlimeM", "SpikeSlimeM", "SpikeSlimeM", "SpikeSlimeM"], 5),
            "Exordium Thugs 1": (["BlueSlaver", "BlueSlaver"], 8),  # Fallback
            "Exordium Thugs 2": (["GreenLouse", "BlueSlaver"], 8),
            "Exordium Thugs 3": (["SpikeSlimeM", "BlueSlaver"], 8),
            "Cultist and Louse": (["Cultist", "GreenLouse"], 10),
            "Thick Slimes": (["SpikeSlimeM", "SpikeSlimeM", "SpikeSlimeM"], 10),
        }
        return {"easy": easy, "hard": hard}

    def _build_elite_pools(self):
        elite = {
            "Gremlin Nob": (["GremlinNob"], 34),
            "Lagavulin": (["Lagavulin"], 33),
            "3 Sentries": (["Sentry", "Sentry", "Sentry"], 33),
        }
        return {"act1": elite}

    def get_pool_name(self, encounter_count: int, act: int = 1) -> str:
        easy_count = self.EASY_ENCOUNTER_COUNTS.get(act, 2)
        return "easy" if encounter_count < easy_count else "hard"

    def _get_available_encounters(self, pool, encounter_history, is_first_hard=False):
        available = {}
        for name, (enemies, weight) in pool.items():
            if name in encounter_history[-2:]:
                continue
            if is_first_hard:
                last = encounter_history[-1] if encounter_history else None
                if name == "3 Louses" and last == "2 Louses":
                    continue
                if name in ["Big Slime", "Lots of Slimes"] and last == "Small Slimes":
                    continue
                if name.startswith("Exordium Thugs") and last == "Looter":
                    continue
            available[name] = (enemies, weight)
        return available

    def _select_weighted_encounter(self, encounters):
        if not encounters:
            return None
        items = list(encounters.items())
        names = [n for n, _ in items]
        weights = [w for _, (_, w) in items]
        return self.rng.choices(names, weights=weights, k=1)[0]

    def _resolve_encounter(self, enemy_names):
        enemy_classes = _get_enemy_classes()
        return [enemy_classes[n]() for n in enemy_names if n in enemy_classes]

    def get_normal_encounter(self, floor: int, encounter_count: int = 0, encounter_history: List[str] = None):
        if encounter_history is None:
            encounter_history = []
        pool_name = self.get_pool_name(encounter_count)
        pool = self.normal_pools.get(pool_name, {})
        is_first_hard = pool_name == "hard" and encounter_count == self.EASY_ENCOUNTER_COUNTS.get(1, 3)
        available = self._get_available_encounters(pool, encounter_history, is_first_hard)
        if not available:
            available = pool
        selected_name = self._select_weighted_encounter(available)
        if not selected_name:
            return [], ""
        enemy_names, _ = available[selected_name]
        return self._resolve_encounter(enemy_names), selected_name

    def get_elite_encounter(self, floor: int, last_elite: str = None):
        elite_classes = _get_elite_classes()
        if not elite_classes:
            return [], ""
        pool = self.elite_pools.get("act1", {})
        available = {n: d for n, d in pool.items() if n != last_elite} if last_elite else pool
        if not available:
            available = pool
        selected_name = self._select_weighted_encounter(available)
        if not selected_name:
            return [], ""
        enemy_names, _ = pool[selected_name]
        enemies = [elite_classes[n]() for n in enemy_names if n in elite_classes]
        return enemies, selected_name

    def get_boss_encounter(self, floor: int):
        return []


def create_encounter_pool(seed: int) -> EncounterPool:
    return EncounterPool(seed)
