"""Act 1 enemies package initialization."""

from .cultist import Cultist
from .jaw_worm import JawWorm
from .spike_slime import SpikeSlimeL, SpikeSlimeM, SpikeSlimeS
from .acid_slime import AcidSlimeL, AcidSlimeM, AcidSlimeS
from .fungi_beast import FungiBeast
from .louse import RedLouse, GreenLouse
from .slaver import BlueSlaver, RedSlaver
from .the_guardian import TheGuardian
from .slime_boss import SlimeBoss
from .the_hexaghost import TheHexaghost
from .lagavulin import Lagavulin
from .gremlin_nob import GremlinNob
from .sentry import Sentry
from .gremlin import (
    FatGremlin,
    SneakyGremlin,
    MadGremlin,
    ShieldGremlin,
    GremlinWizard,
)

__all__ = [
    # Common enemies
    'Cultist',
    'JawWorm',
    'SpikeSlimeL',
    'SpikeSlimeM',
    'SpikeSlimeS',
    'AcidSlimeL',
    'AcidSlimeM',
    'AcidSlimeS',
    'RedLouse',
    'GreenLouse',
    'BlueSlaver',
    'RedSlaver',
    'FatGremlin',
    'SneakyGremlin',
    'MadGremlin',
    'ShieldGremlin',
    'GremlinWizard',
    # Elite enemies
    'FungiBeast',
    'Lagavulin',
    'GremlinNob',
    'Sentry',
    # Boss enemies
    'TheGuardian',
    'SlimeBoss',
    'TheHexaghost',
]
