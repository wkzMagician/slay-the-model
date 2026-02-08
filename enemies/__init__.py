"""
Enemies package initialization
"""
from .base import Enemy

# Act 1 Enemies
from .act1 import Cultist, JawWorm, SpikeSlime, SpikeSlimeM

# Export all enemies
__all__ = [
    # Base class
    'Enemy',
    
    # Act 1 Common
    'Cultist',
    'JawWorm',
    'SpikeSlime',
    'SpikeSlimeM',
]

__all_names__ = __all__
