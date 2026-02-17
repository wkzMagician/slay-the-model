"""
Enemies package initialization
"""
from .base import Enemy

# Act 1 Enemies
from .act1 import (
    Cultist, JawWorm, SpikeSlime, SpikeSlimeM,
    FungiBeast, RedLouse, GreenLouse,
    BlueSlaver, RedSlaver,
    TheGuardian, SlimeBoss, TheHexaghost,
    Lagavulin, GremlinNob, Sentry
)

# Export all enemies
__all__ = [
    # Base class
    'Enemy',
    
    # Act 1 Common
    'Cultist',
    'JawWorm',
    'SpikeSlime',
    'SpikeSlimeM',
    'RedLouse',
    'GreenLouse',
    'BlueSlaver',
    'RedSlaver',
    
    # Act 1 Elite
    'FungiBeast',
    'Lagavulin',
    'GremlinNob',
    'Sentry',
    
    # Act 1 Boss
    'TheGuardian',
    'SlimeBoss',
    'TheHexaghost',
]

__all_names__ = __all__
