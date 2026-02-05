"""
Global relics package - relics available to all character classes.
"""

# Import all global relics
from .anchor import Anchor
from .bag_of_preparation import BagOfPreparation
from .burning_blood import BurningBlood
from .vajra import Vajra
from .sisyphus import Sisyphus

__all__ = [
    'Anchor',
    'BagOfPreparation',
    'BurningBlood',
    'Vajra',
    'Sisyphus',
]
