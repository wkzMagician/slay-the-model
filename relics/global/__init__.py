"""
Global relics package - relics available to all character classes.
Organized by rarity.
"""

# Import all global relics from rarity-based files
from .common import (
    Anchor,
    BagOfPreparation,
    BurningBlood,
    Vajra,
    BlackStar
)

from .uncommon import (
    Akara,
    BrassLantern,
    CeramicFigurine,
    CoffeeDripper,
    HookAndRope,
    StrangeSpoon,
    Sisyphus
)

from .rare import (
    VajraBoss,
    RedMask,
    MummyHand,
    Dagger,
    MutagenicStrength
)

from .boss import (
    BurningBloodBoss,
    SneckoEye,
    ChampionsBelt,
    FrozenCore,
    DeadBranch,
    MawBank,
    TheCourier,
    BlueCandle,
    RuneCube,
    BlackBloodBoss,
    TheHeart
)

from .shop import MembershipCard

__all__ = [
    # Common (5)
    'Anchor',
    'BagOfPreparation',
    'BurningBlood',
    'Vajra',
    'BlackStar',

    # Uncommon (7)
    'Akara',
    'BrassLantern',
    'CeramicFigurine',
    'CoffeeDripper',
    'HookAndRope',
    'StrangeSpoon',
    'Sisyphus',

    # Rare (5)
    'VajraBoss',
    'RedMask',
    'MummyHand',
    'Dagger',
    'MutagenicStrength',

    # Boss (11)
    'BurningBloodBoss',
    'SneckoEye',
    'ChampionsBelt',
    'FrozenCore',
    'DeadBranch',
    'MawBank',
    'TheCourier',
    'BlueCandle',
    'RuneCube',
    'BlackBloodBoss',
    'TheHeart',

    # Shop (1)
    'MembershipCard',
]