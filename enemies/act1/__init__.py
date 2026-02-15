"""Act 1 enemies package initialization."""

from .cultist import Cultist
from .jaw_worm import JawWorm
from .spike_slime import SpikeSlime, SpikeSlimeM
from .fungi_beast import FungiBeast
from .louse import RedLouse, GreenLouse
from .slaver import BlueSlaver, RedSlaver
from .the_guardian import TheGuardian
from .slime_boss import SlimeBoss
from .the_hexaghost import TheHexaghost

__all__ = [
    # Common enemies
    'Cultist',
    'JawWorm',
    'SpikeSlime',
    'SpikeSlimeM',
    'RedLouse',
    'GreenLouse',
    'BlueSlaver',
    'RedSlaver',
    # Elite enemies
    'FungiBeast',
    # Boss enemies
    'TheGuardian',
    'SlimeBoss',
    'TheHexaghost',
]
