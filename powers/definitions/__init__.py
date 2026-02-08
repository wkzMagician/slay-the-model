"""
All game power definitions.
Powers are temporary or permanent combat effects.
"""
from powers.definitions.strength import StrengthPower
from powers.definitions.vulnerable import VulnerablePower
from powers.definitions.weak import WeakPower
from powers.definitions.flex import FlexPower
from powers.definitions.heavy_blade import HeavyBladePower

__all__ = [
    "StrengthPower",
    "VulnerablePower",
    "WeakPower",
    "FlexPower",
    "HeavyBladePower",
]