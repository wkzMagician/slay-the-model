"""
Global relics package - relics available to all character classes.
"""

# Import all global relics
from .anchor import Anchor
from .bag_of_preparation import BagOfPreparation
from .burning_blood import BurningBlood
from .vajra import Vajra
from .black_star import BlackStar
from .brass_lantern import BrassLantern
from .ceramic_figurine import CeramicFigurine
from .coffee_dripper import CoffeeDripper
from .hook_and_rope import HookAndRope
from .strange_spoon import StrangeSpoon
from .sisyphus import Sisyphus
from .red_mask import RedMask
from .mummy_hand import MummyHand

# Uncommon Relics (5)
from .akara import Akara
from .brass_lantern import BrassLantern
from .ceramic_figurine import CeramicFigurine
from .coffee_dripper import CoffeeDripper
from .strange_spoon import StrangeSpoon
from .hook_and_rope import HookAndRope

# Rare Relics (5)
from .vajra_boss import VajraBoss
from .red_mask import RedMask
from .mummy_hand import MummyHand
from .dagger import Dagger
from .mutagenic_strength import MutagenicStrength

# Boss Relics (15)
from .burning_blood_boss import BurningBloodBoss
from .snecko_eye import SneckoEye
from .champions_belt import ChampionsBelt
from .frozen_core import FrozenCore
from .dead_branch import DeadBranch
from .maw_bank import MawBank
from .the_courier import TheCourier
from .blue_candle import BlueCandle
from .rune_cube import RuneCube
from .black_blood_boss import BlackBloodBoss
from .the_heart import TheHeart

# Shop Relics (1)
from .membership_card import MembershipCard

__all__ = [
    # Common (5)
    'Anchor',
    'BagOfPreparation',
    'BurningBlood',
    'Vajra',
    'BlackStar',

    # Uncommon (10)
    'BrassLantern',
    'CeramicFigurine',
    'CoffeeDripper',
    'StrangeSpoon',
    'HookAndRope',
    'Sisyphus',
    'Akara',
    'RedMask',
    'MummyHand',

    # Rare (5)
    'VajraBoss',
    'Dagger',
    'MutagenicStrength',

    # Boss (15)
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

