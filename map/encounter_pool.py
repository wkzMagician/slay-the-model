# -*- coding: utf-8 -*-
"""Encounter pool system for selecting enemies.

Rules of Monster Encounters:
- First 3 encounters (Act 1) or 2 (other acts) = Easy Pool
- Remaining encounters = Hard Pool
- Same encounter cannot appear in next 2 encounters
- Act 1 specific constraints for first Hard Pool
- Elites cannot be same twice in a row

Dynamic Enemy Initialization:
- Encounters use factory functions that can pass parameters
- Support for random enemy variants (e.g., Red/Green Louse 50/50)
- Support for initial powers/intents on enemies
"""

from typing import Dict, List, Tuple, Optional, Callable, Any
from utils.types import EnemyType
from utils.registry import register
import random


EnemyFactory = Callable[[], List[Any]]


def _create_louse_pair():
    """Create 2 louses, each independently 50% red or green."""
    from enemies.act1.louse import RedLouse, GreenLouse
    rng = random.Random()
    louses = []
    for _ in range(2):
        if rng.random() < 0.5:
            louses.append(RedLouse())
        else:
            louses.append(GreenLouse())
    return louses


def _create_triple_louse():
    """Create 3 louses, each independently 50% red or green."""
    from enemies.act1.louse import RedLouse, GreenLouse
    rng = random.Random()
    louses = []
    for _ in range(3):
        if rng.random() < 0.5:
            louses.append(RedLouse())
        else:
            louses.append(GreenLouse())
    return louses


def _create_small_slimes():
    """Create 2 small slimes: either (Spike Slime M + Acid Slime S) 
    or (Acid Slime M + Spike Slime S)."""
    from enemies.act1.spike_slime import SpikeSlimeM, SpikeSlimeS
    from enemies.act1.acid_slime import AcidSlimeM, AcidSlimeS
    
    rng = random.Random()
    if rng.random() < 0.5:
        return [SpikeSlimeM(), AcidSlimeS()]
    else:
        return [AcidSlimeM(), SpikeSlimeS()]


def _create_large_slime():
    """Create Spike Slime (AcidSlime not implemented yet)."""
    from enemies.act1.spike_slime import SpikeSlimeL
    return [SpikeSlimeL()]


def _create_swarm_slimes():
    """Create 5 medium spike slimes (AcidSlime not implemented yet)."""
    from enemies.act1.spike_slime import SpikeSlimeS
    from enemies.act1.acid_slime import AcidSlimeS

    slimes = [SpikeSlimeS() for _ in range(3)] + [AcidSlimeS() for _ in range(2)]
    rng = random.Random()
    rng.shuffle(slimes)
    return slimes


def _create_gremlin_gang():
    """Create 4 random gremlins from the pool."""
    from enemies.act1.gremlin import (
        FatGremlin, SneakyGremlin, MadGremlin, ShieldGremlin, GremlinWizard
    )
    rng = random.Random()

    valid_compositions = [
        [FatGremlin, FatGremlin, SneakyGremlin, SneakyGremlin],
        [FatGremlin, FatGremlin, MadGremlin, MadGremlin],
        [SneakyGremlin, SneakyGremlin, MadGremlin, MadGremlin],
        [FatGremlin, FatGremlin, ShieldGremlin, GremlinWizard],
        [SneakyGremlin, SneakyGremlin, ShieldGremlin, GremlinWizard],
        [MadGremlin, MadGremlin, ShieldGremlin, GremlinWizard],
    ]

    selected_composition = list(rng.choice(valid_compositions))
    rng.shuffle(selected_composition)
    return [gremlin_cls() for gremlin_cls in selected_composition]


def _create_looter():
    """Create Looter encounter."""
    from enemies.act1.looter import Looter
    return [Looter()]


def _create_exordium_thugs():
    """Create Exordium Thugs encounter."""
    from enemies.act1.louse import RedLouse, GreenLouse
    from enemies.act1.spike_slime import SpikeSlimeM
    from enemies.act1.slaver import BlueSlaver, RedSlaver
    from enemies.act1.looter import Looter
    rng = random.Random()
    first_pool = [RedLouse, GreenLouse, SpikeSlimeM]
    second_pool = [BlueSlaver, RedSlaver, Looter]
    return [rng.choice(first_pool)(), rng.choice(second_pool)()]


def _create_exordium_wildlife():
    """Create Exordium Wildlife encounter."""
    from enemies.act1.fungi_beast import FungiBeast
    from enemies.act1.jaw_worm import JawWorm
    from enemies.act1.louse import RedLouse, GreenLouse
    from enemies.act1.spike_slime import SpikeSlimeM
    rng = random.Random()
    first_pool = [FungiBeast, JawWorm]
    second_pool = [RedLouse, GreenLouse, SpikeSlimeM]
    return [rng.choice(first_pool)(), rng.choice(second_pool)()]


def _create_boss_guardian():
    """Create The Guardian boss with initial powers."""
    from enemies.act1.the_guardian import TheGuardian
    return [TheGuardian()]


def _create_boss_slime():
    """Create Slime Boss with initial powers."""
    from enemies.act1.slime_boss import SlimeBoss
    return [SlimeBoss()]


def _create_boss_hexaghost():
    """Create The Hexaghost boss with initial powers."""
    from enemies.act1.the_hexaghost import TheHexaghost
    return [TheHexaghost()]


def _create_lagavulin():
    """Create Lagavulin elite with Metallicize and sleep state."""
    from enemies.act1.lagavulin import Lagavulin
    return [Lagavulin()]


def _create_gremlin_nob():
    """Create Gremlin Nob elite."""
    from enemies.act1.gremlin_nob import GremlinNob
    return [GremlinNob()]


def _create_sentries():
    """Create 3 Sentries elite encounter."""
    from enemies.act1.sentry import Sentry
    return [Sentry(is_middle=False), Sentry(is_middle=True), Sentry(is_middle=False)]


# Act 2 encounter factory functions
def _create_snecko():
    from enemies.act2.snecko import Snecko
    return [Snecko()]


def _create_snake_plant():
    from enemies.act2.snake_plant import SnakePlant
    return [SnakePlant()]


def _create_shelled_parasite():
    from enemies.act2.shelled_parasite import ShelledParasite
    return [ShelledParasite()]


def _create_chosen():
    from enemies.act2.chosen import Chosen
    return [Chosen()]


def _create_cultist_chosen():
    from enemies.act1.cultist import Cultist
    from enemies.act2.chosen import Chosen
    return [Cultist(), Chosen()]


def _create_spheric_guardian():
    from enemies.act2.spheric_guardian import SphericGuardian
    return [SphericGuardian()]


def _create_centurion_mystic():
    from enemies.act2.centurion import Centurion
    from enemies.act2.mystic import Mystic
    return [Centurion(), Mystic()]


# Act 2 new factory functions for updated encounter pool
def _create_three_byrds():
    """Create 3 Byrds encounter."""
    from enemies.act2.byrd import Byrd
    return [Byrd(), Byrd(), Byrd()]


def _create_two_thieves():
    """Create 2 Thieves: Looter on left, Mugger on right."""
    from enemies.act1.looter import Looter
    from enemies.act2.mugger import Mugger
    return [Looter(), Mugger()]


def _create_chosen_byrd():
    """Create Chosen and Byrd encounter."""
    from enemies.act2.chosen import Chosen
    from enemies.act2.byrd import Byrd
    return [Chosen(), Byrd()]


def _create_sentry_spheric_guardian():
    """Create Sentry and Spheric Guardian encounter."""
    from enemies.act1.sentry import Sentry
    from enemies.act2.spheric_guardian import SphericGuardian
    return [Sentry(), SphericGuardian()]


def _create_three_cultists():
    """Create 3 Cultists encounter."""
    from enemies.act1.cultist import Cultist
    return [Cultist(), Cultist(), Cultist()]


def _create_shelled_parasite_fungi():
    """Create Shelled Parasite and Fungi Beast encounter."""
    from enemies.act2.shelled_parasite import ShelledParasite
    from enemies.act1.fungi_beast import FungiBeast
    return [ShelledParasite(), FungiBeast()]


# Act 2 elite factory functions
def _create_book_of_stabbing():
    from enemies.act2.book_of_stabbing import BookOfStabbing
    return [BookOfStabbing()]


def _create_gremlin_leader():
    from enemies.act2.gremlin_leader import GremlinLeader
    return [GremlinLeader()]


def _create_taskmaster():
    """Create Taskmaster with Blue Slaver and Red Slaver.
    
    Order: BlueSlaver - Taskmaster - RedSlaver
    """
    from enemies.act2.taskmaster import Taskmaster
    from enemies.act1.slaver import BlueSlaver, RedSlaver
    return [BlueSlaver(), Taskmaster(), RedSlaver()]


def _create_bronze_automaton():
    from enemies.act2.bronze_automaton import BronzeAutomaton
    from enemies.act2.bronze_orb import BronzeOrb
    return [BronzeAutomaton()]

def _create_boss_champ():
    from enemies.act2.the_champ import TheChamp
    return [TheChamp()]

def _create_boss_collector():
    from enemies.act2.the_collector import TheCollector
    return [TheCollector()]


# Act 3 encounter factory functions
def _create_spire_growth():
    """Create Spire Growth encounter."""
    from enemies.act3.spire_growth import SpireGrowth
    return [SpireGrowth()]


def _create_orb_walker():
    """Create Orb Walker encounter."""
    from enemies.act3.orb_walker import OrbWalker
    return [OrbWalker()]


def _create_darkling():
    """Create 3 Darklings encounter."""
    from enemies.act3.darkling import Darkling
    return [Darkling(), Darkling(), Darkling()]


def _create_three_shapes():
    """Create 3 Shapes from pool (2x Repulsor, 2x Exploder, 2x Spiker)."""
    from enemies.act3.repulsor import Repulsor
    from enemies.act3.exploder import Exploder
    from enemies.act3.spiker import Spiker
    rng = random.Random()
    pool = [Repulsor, Repulsor, Exploder, Exploder, Spiker, Spiker]
    selected = rng.sample(pool, 3)
    return [cls() for cls in selected]


def _create_four_shapes():
    """Create 4 Shapes from pool (2x Repulsor, 2x Exploder, 2x Spiker)."""
    from enemies.act3.repulsor import Repulsor
    from enemies.act3.exploder import Exploder
    from enemies.act3.spiker import Spiker
    rng = random.Random()
    pool = [Repulsor, Repulsor, Exploder, Exploder, Spiker, Spiker]
    selected = rng.sample(pool, 4)
    return [cls() for cls in selected]


def _create_spheric_guardian_two_shapes():
    """Create Spheric Guardian and 2 Shapes from pool."""
    from enemies.act2.spheric_guardian import SphericGuardian
    from enemies.act3.repulsor import Repulsor
    from enemies.act3.exploder import Exploder
    from enemies.act3.spiker import Spiker
    rng = random.Random()
    pool = [Repulsor, Repulsor, Exploder, Exploder, Spiker, Spiker]
    selected = rng.sample(pool, 2)
    return [SphericGuardian()] + [cls() for cls in selected]


def _create_jaw_worm_horde():
    """Create 3 Jaw Worms with strength and block buffs (Act 3 hard version)."""
    from enemies.act1.jaw_worm import JawWorm
    return [JawWorm(is_hard=True), JawWorm(is_hard=True), JawWorm(is_hard=True)]


def _create_the_maw():
    """Create The Maw encounter."""
    from enemies.act3.the_maw import TheMaw
    return [TheMaw()]


def _create_transient():
    """Create Transient encounter."""
    from enemies.act3.transient import Transient
    return [Transient()]


def _create_writhing_mass():
    """Create Writhing Mass encounter."""
    from enemies.act3.writhing_mass import WrithingMass
    return [WrithingMass()]


# Act 3 elite factory functions
def _create_giant_head():
    """Create Giant Head elite."""
    from enemies.act3.giant_head import GiantHead
    return [GiantHead()]


def _create_nemesis():
    """Create Nemesis elite."""
    from enemies.act3.nemesis import Nemesis
    return [Nemesis()]


# Act 3 boss factory functions
def _create_boss_time_eater():
    """Create Time Eater boss."""
    from enemies.act3.time_eater import TimeEater
    return [TimeEater()]


def _create_boss_awakened_one():
    """Create Awakened One boss."""
    from enemies.act3.awakened_one import AwakenedOne
    return [AwakenedOne()]


def _create_boss_donu_deca():
    """Create Donu and Deca boss encounter.
    
    Order: Donu - Deca
    """
    from enemies.act3.donu import Donu
    from enemies.act3.deca import Deca
    return [Donu(), Deca()]


# Act 4 encounter factory functions
# Note: Act 4 has no normal enemies, only elites and boss

def _create_spire_shield_spear():
    """Create Spire Shield and Spire Spear elite encounter.
    
    Order: SpireShield - SpireSpear (player in middle)
    """
    from enemies.act4.spire_shield import SpireShield
    from enemies.act4.spire_spear import SpireSpear
    return [SpireShield(), SpireSpear()]


def _create_boss_corrupt_heart():
    """Create Corrupt Heart final boss."""
    from enemies.act4.corrupt_heart import CorruptHeart
    return [CorruptHeart()]

class EncounterPool:
    """Manages enemy encounter selection based on game rules."""
    
    EASY_ENCOUNTER_COUNTS = {1: 3, 2: 2, 3: 2}
    
    ACT1_EASY_POOL = {
        "Cultist": (lambda: [__import__("enemies.act1.cultist", fromlist=["Cultist"]).Cultist()], 2),
        "Jaw Worm": (lambda: [__import__("enemies.act1.jaw_worm", fromlist=["JawWorm"]).JawWorm()], 2),
        "2 Louse": (_create_louse_pair, 2),
        "Small Slimes": (_create_small_slimes, 2),
    }
    
    ACT1_HARD_POOL = {
        "Gang of Gremlins": (_create_gremlin_gang, 1),
        "Large Slime": (_create_large_slime, 2),
        "Swarm of Slimes": (_create_swarm_slimes, 1),
        "Blue Slaver": (lambda: [__import__("enemies.act1.slaver", fromlist=["BlueSlaver"]).BlueSlaver()], 1),
        "Red Slaver": (lambda: [__import__("enemies.act1.slaver", fromlist=["RedSlaver"]).RedSlaver()], 1),
        "3 Louse": (_create_triple_louse, 2),
        "2 Fungi Beasts": (lambda: [__import__("enemies.act1.fungi_beast", fromlist=["FungiBeast"]).FungiBeast() for _ in range(2)], 2),
        "Exordium Thugs": (_create_exordium_thugs, 1.5),
        "Exordium Wildlife": (_create_exordium_wildlife, 1.5),
        "Looter": (_create_looter, 2),
    }
    
    ACT1_ELITE_POOL = {
        "Gremlin Nob": (_create_gremlin_nob, 1),
        "Lagavulin": (_create_lagavulin, 1),
        "3 Sentries": (_create_sentries, 1),
    }
    
    ACT2_EASY_POOL = {
        "Spheric Guardian": (_create_spheric_guardian, 2),
        "Chosen": (_create_chosen, 2),
        "Shelled Parasite": (_create_shelled_parasite, 2),
        "3 Byrds": (_create_three_byrds, 2),
        "2 Thieves": (_create_two_thieves, 2),
    }
    
    ACT2_HARD_POOL = {
        "Chosen and Byrds": (_create_chosen_byrd, 2),
        "Cultist and Chosen": (_create_cultist_chosen, 3),
        "Sentry and Spheric Guardian": (_create_sentry_spheric_guardian, 2),
        "Snake Plant": (_create_snake_plant, 6),
        "Snecko": (_create_snecko, 4),
        "Centurion and Mystic": (_create_centurion_mystic, 6),
        "3 Cultists": (_create_three_cultists, 3),
        "Shelled Parasite and Fungi": (_create_shelled_parasite_fungi, 3),
    }
    
    ACT2_ELITE_POOL = {
        "Book of Stabbing": (_create_book_of_stabbing, 1),
        "Gremlin Leader": (_create_gremlin_leader, 1),
        "Taskmaster": (_create_taskmaster, 1),
    }
    
    # Act 3 encounter pools
    # Easy Pool (first 2 encounters)
    ACT3_EASY_POOL = {
        "3 Darklings": (_create_darkling, 2),
        "Orb Walker": (_create_orb_walker, 2),
        "3 Shapes": (_create_three_shapes, 2),
    }
    
    # Hard Pool (remaining encounters)
    ACT3_HARD_POOL = {
        "4 Shapes": (_create_four_shapes, 1),
        "The Maw": (_create_the_maw, 1),
        "Spheric Guardian and 2 Shapes": (_create_spheric_guardian_two_shapes, 1),
        "3 Darklings": (_create_darkling, 1),
        "Spire Growth": (_create_spire_growth, 1),
        "Transient": (_create_transient, 1),
        "Jaw Worm Horde": (_create_jaw_worm_horde, 1),
        "Writhing Mass": (_create_writhing_mass, 1),
    }
    
    ACT3_ELITE_POOL = {
        "Giant Head": (_create_giant_head, 1),
        "Nemesis": (_create_nemesis, 1),
    }
    
    # Act 4 encounter pools
    # Note: Act 4 has no normal enemy encounters, only elites and boss
    ACT4_EASY_POOL = {}
    ACT4_HARD_POOL = {}
    
    ACT4_ELITE_POOL = {
        "Spire Shield and Spire Spear": (_create_spire_shield_spear, 1),
    }
    
    # Act-specific boss pools
    # Each act has 3 possible bosses, one is randomly selected at start
    ACT1_BOSS_POOL = {
        "The Guardian": _create_boss_guardian,
        "Slime Boss": _create_boss_slime,
        "The Hexaghost": _create_boss_hexaghost,
    }
    
    ACT2_BOSS_POOL = {
        "Bronze Automaton": _create_bronze_automaton,
        "The Collector": _create_boss_collector,
        "The Champ": _create_boss_champ,
    }
    
    ACT3_BOSS_POOL = {
        "Time Eater": _create_boss_time_eater,
        "Awakened One": _create_boss_awakened_one,
        "Donu and Deca": _create_boss_donu_deca,
    }
    
    ACT4_BOSS_POOL = {
        "Corrupt Heart": _create_boss_corrupt_heart,
    }
    
    # Alias for backwards compatibility
    BOSS_POOL = ACT1_BOSS_POOL

    def __init__(self, seed: int, act_id: int = 1):
        self.rng = random.Random(seed)
        self.act_id = act_id
        self._load_act_pools(act_id)
    
    def _load_act_pools(self, act_id: int):
        """Load encounter pools for specific act."""
        pools = {
            1: (self.ACT1_EASY_POOL, self.ACT1_HARD_POOL, self.ACT1_ELITE_POOL, self.ACT1_BOSS_POOL),
            2: (self.ACT2_EASY_POOL, self.ACT2_HARD_POOL, self.ACT2_ELITE_POOL, self.ACT2_BOSS_POOL),
            3: (self.ACT3_EASY_POOL, self.ACT3_HARD_POOL, self.ACT3_ELITE_POOL, self.ACT3_BOSS_POOL),
            4: (self.ACT4_EASY_POOL, self.ACT4_HARD_POOL, self.ACT4_ELITE_POOL, self.ACT4_BOSS_POOL),
        }
        (self.easy_pool, self.hard_pool, 
         self.elite_pool, self.boss_pool) = pools.get(act_id, pools[1])

    def get_pool_name(self, encounter_count: int, act: int = 1) -> str:
        """Determine if current encounter should be from easy or hard pool."""
        easy_count = self.EASY_ENCOUNTER_COUNTS.get(act, 2)
        return "easy" if encounter_count < easy_count else "hard"

    def _get_available_encounters(self, pool, encounter_history, is_first_hard=False, last_encounter=None):
        """Filter out recently used encounters."""
        available = {}
        for name, (factory, weight) in pool.items():
            if name in encounter_history[-2:]:
                continue
            if is_first_hard and last_encounter:
                if name == "3 Louse" and last_encounter == "2 Louse":
                    continue
                if name in ["Large Slime", "Swarm of Slimes"] and last_encounter == "Small Slimes":
                    continue
                if name == "Exordium Thugs" and last_encounter == "Looter":
                    continue
            available[name] = (factory, weight)
        return available

    def _select_weighted_encounter(self, encounters):
        """Select an encounter using weighted random selection."""
        if not encounters:
            return None
        items = list(encounters.items())
        names = [n for n, _ in items]
        weights = [w for _, (_, w) in items]
        return self.rng.choices(names, weights=weights, k=1)[0]

    def get_normal_encounter(self, floor, encounter_count=0, encounter_history=None):
        """Get a normal (non-elite, non-boss) encounter."""
        if encounter_history is None:
            encounter_history = []
        pool_name = self.get_pool_name(encounter_count)
        pool = self.easy_pool if pool_name == "easy" else self.hard_pool
        is_first_hard = pool_name == "hard" and encounter_count == self.EASY_ENCOUNTER_COUNTS.get(1, 3)
        last_encounter = encounter_history[-1] if encounter_history else None
        available = self._get_available_encounters(pool, encounter_history, is_first_hard, last_encounter)
        if not available:
            available = pool
        selected_name = self._select_weighted_encounter(available)
        if not selected_name:
            return [], ""
        factory, _ = available[selected_name]
        enemies = factory()
        return enemies, selected_name

    def get_elite_encounter(self, floor, last_elite=None):
        """Get an elite encounter."""
        available = {name: data for name, data in self.elite_pool.items() if name != last_elite}
        if not available:
            available = self.elite_pool
        selected_name = self._select_weighted_encounter(available)
        if not selected_name:
            return [], ""
        factory, _ = self.elite_pool[selected_name]
        enemies = factory()
        return enemies, selected_name

    def get_boss_encounter(self, floor, boss_index=0):
        """Get a boss encounter for the current act.
        
        Args:
            floor: Floor within act (0-indexed), expects 15 or 16 for boss floors
            boss_index: For A20 Act 3 double boss, 0=first boss, 1=second boss
        """
        from engine.game_state import game_state
        
        is_act3_a20 = self.act_id == 3 and game_state.ascension >= 20
        
        if is_act3_a20:
            if floor not in [15, 16]:
                return [], ""
        else:
            if floor != 15:
                return [], ""
        
        boss_names = list(self.boss_pool.keys())
        
        if is_act3_a20 and boss_index == 0:
            boss_name = self.rng.choice(boss_names)
            self._act3_first_boss_name = boss_name
        elif is_act3_a20 and boss_index == 1:
            if not hasattr(self, '_act3_first_boss_name'):
                self._act3_first_boss_name = self.rng.choice(boss_names)
            remaining = [n for n in boss_names if n != self._act3_first_boss_name]
            boss_name = self.rng.choice(remaining) if remaining else self.rng.choice(boss_names)
        else:
            boss_name = self.rng.choice(boss_names)
        
        factory = self.boss_pool[boss_name]
        enemies = factory()
        return enemies, boss_name


def create_encounter_pool(seed: int) -> EncounterPool:
    """Factory function to create an encounter pool with the given seed."""
    return EncounterPool(seed)
