"""
Enemies package initialization
"""
from .base import Enemy

# Act 1 Enemies
from .act1 import Cultist, JawWorm, FungiBeast, LouseSlaver
from .act1 import TheGuardian, SlimeBoss, TheHexaghost
from .act1 import SpikeSlime, SpikeSlimeM

# Export all enemies
__all__ = [
    # Base class
    'Enemy',
    
    # Act 1 Common
    'Cultist',
    'JawWorm',
    'LouseSlaver',
    'SpikeSlime',
    'SpikeSlimeM',
    
    # Act 1 Elite
    'FungiBeast',
    
    # Act 1 Boss
    'TheGuardian',
    'SlimeBoss',
    'TheHexaghost',
]

__all_names__ = __all__
