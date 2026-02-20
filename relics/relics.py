"""Relic helper functions."""

import random
from typing import Optional, List, Type
from utils.types import RarityType

# Import relic classes by rarity
from relics.global_relics.common import (
    Akabeko, Anchor, AncientTeaSet, BagOfPreparation, Vajra,
    ArtOfWar, BagOfMarbles, BloodVial, BronzeScales, CentennialPuzzle
)
from relics.global_relics.uncommon import (
    HornCleat, BlueCandle, BottledFlame, BottledLightning, BottledTornado,
    DarkstonePeriapt, EternalFeather, FrozenEgg, GremlinHorn, InkBottle
)
from relics.global_relics.rare import (
    BirdFacedUrn, Calipers, CaptainsWheel, DeadBranch, DuVuDoll,
    FossilizedHelix, Ginger, Girya, IceCream, LizardTail
)
from relics.global_relics.boss import (
    SneckoEye, Astrolabe, BlackStar, BlackBlood, BustedCrown,
    CallingBell, CoffeeDripper, CursedKey, Ectoplasm, EmptyCage
)

# Map of relic classes by rarity
RELICS_BY_RARITY = {
    RarityType.COMMON: [
        Akabeko, Anchor, AncientTeaSet, BagOfPreparation, Vajra,
        ArtOfWar, BagOfMarbles, BloodVial, BronzeScales, CentennialPuzzle
    ],
    RarityType.UNCOMMON: [
        HornCleat, BlueCandle, BottledFlame, BottledLightning, BottledTornado,
        DarkstonePeriapt, EternalFeather, FrozenEgg, GremlinHorn, InkBottle
    ],
    RarityType.RARE: [
        BirdFacedUrn, Calipers, CaptainsWheel, DeadBranch, DuVuDoll,
        FossilizedHelix, Ginger, Girya, IceCream, LizardTail
    ],
    RarityType.BOSS: [
        SneckoEye, Astrolabe, BlackStar, BlackBlood, BustedCrown,
        CallingBell, CoffeeDripper, CursedKey, Ectoplasm, EmptyCage
    ],
}


def get_random_relic_by_rarity(rarity: RarityType, count: int = 1) -> List[Type]:
    """Get random relic classes by rarity.
    
    Args:
        rarity: The rarity type to filter relics
        count: Number of relics to return (default 1)
    
    Returns:
        List of relic classes
    """
    relics = RELICS_BY_RARITY.get(rarity, [])
    if not relics:
        return []
    
    return random.sample(relics, min(count, len(relics)))


def get_single_random_relic_by_rarity(rarity: RarityType) -> Optional[Type]:
    """Get a single random relic class by rarity.
    
    Args:
        rarity: The rarity type to filter relics
    
    Returns:
        A relic class or None if no relics of that rarity
    """
    relics = get_random_relic_by_rarity(rarity, count=1)
    return relics[0] if relics else None


def create_relic_instance(relic_class: Type):
    """Create an instance of a relic class.
    
    Args:
        relic_class: The relic class to instantiate
    
    Returns:
        An instance of the relic
    """
    return relic_class()
