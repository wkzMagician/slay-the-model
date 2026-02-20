"""
Enemies package initialization
"""
from .base import Enemy

# Act 1 Enemies
from .act1 import (
    Cultist, JawWorm, 
    SpikeSlimeL, SpikeSlimeM, SpikeSlimeS,
    AcidSlimeL, AcidSlimeM, AcidSlimeS,
    FungiBeast, RedLouse, GreenLouse,
    BlueSlaver, RedSlaver,
    TheGuardian, SlimeBoss, TheHexaghost,
    Lagavulin, GremlinNob, Sentry
)

# Act 2 Enemies
from .act2 import (
    Byrd, Chosen, Mugger, ShelledParasite,
    SphericGuardian, Centurion, Mystic,
    SnakePlant, Snecko,
    BookOfStabbing, GremlinLeader, Taskmaster,
    TheCollector, TorchHead, TheChamp,
    BronzeAutomaton, BronzeOrb
)

# Act 3 Enemies
from .act3 import (
    Exploder, OrbWalker, Darkling, Spiker,
    SpireGrowth, Repulsor, Transient,
    WrithingMass, Reptomancer, Dagger,
    GiantHead, Nemesis,
    TimeEater, AwakenedOne
)

# Export all enemies
__all__ = [
    # Base class
    'Enemy',
    
    # Act 1 Common
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
    
    # Act 1 Elite
    'FungiBeast',
    'Lagavulin',
    'GremlinNob',
    'Sentry',
    
    # Act 1 Boss
    'TheGuardian',
    'SlimeBoss',
    'TheHexaghost',
    
    # Act 2 Common
    'Byrd',
    'Chosen',
    'Mugger',
    'ShelledParasite',
    'SphericGuardian',
    'Centurion',
    'Mystic',
    'SnakePlant',
    'Snecko',
    
    # Act 2 Elite
    'BookOfStabbing',
    'GremlinLeader',
    'Taskmaster',
    'TheCollector',
    'TorchHead',
    'TheChamp',
    
    # Act 2 Boss
    'BronzeAutomaton',
    'BronzeOrb',
    
    # Act 3 Normal
    'Exploder',
    'OrbWalker',
    'Darkling',
    'Spiker',
    'SpireGrowth',
    'Repulsor',
    'Transient',
    'WrithingMass',
    'Reptomancer',
    'Dagger',
    
    # Act 3 Elite
    'GiantHead',
    'Nemesis',
    
    # Act 3 Boss
    'TimeEater',
    'AwakenedOne',
]

__all_names__ = __all__
