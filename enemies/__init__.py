"""
Enemies package initialization
"""
# Common Enemies
from .cultist import Cultist
from .jaw_worm import JawWorm
from .fungi_beast import FungiBeast

# Elite Enemies
from .fungi_beast import FungiBeast

# Boss Enemies
from .the_guardian import TheGuardian
from .slime_boss import SlimeBoss

# Final Boss
from .the_hexaghost import TheHexaghost

# Export all enemies
__all__ = [
    # Common (2)
    'Cultist',
    'JawWorm',
    
    # Elite (1)
    'FungiBeast',
    
    # Boss (2)
    'TheGuardian',
    'SlimeBoss',
    'TheHexaghost',
]

__all_names__ = [enemy.__name__ for enemy in __all__]
