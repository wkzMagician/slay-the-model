"""
Ironclad card package - warrior class cards
All Ironclad cards are imported here for registration
"""

# Starter deck cards
from cards.ironclad.strike import Strike
from cards.ironclad.defend import Defend
from cards.ironclad.bash import Bash
from cards.ironclad.anger import Anger

# Common cards
from cards.ironclad.iron_wave import IronWave
from cards.ironclad.pommel_strike import PommelStrike
from cards.ironclad.heavy_blade import HeavyBlade
from cards.ironclad.armaments import Armaments
from cards.ironclad.flex import Flex

# Uncommon cards
from cards.ironclad.clothesline import Clothesline
from cards.ironclad.severe_strike import SevereStrike
from cards.ironclad.inflame import Inflame
from cards.ironclad.body_slam import BodySlam
from cards.ironclad.carnage import Carnage

# Rare cards
from cards.ironclad.bludgeon import Bludgeon
from cards.ironclad.limit_break import LimitBreak
from cards.ironclad.pummel import Pummel
from cards.ironclad.uppercut import Uppercut
from cards.ironclad.offering import Offering

__all__ = [
    # Starter
    'Strike', 'Defend', 'Bash', 'Anger',
    # Common
    'IronWave', 'PommelStrike', 'HeavyBlade', 'Armaments', 'Flex',
    # Uncommon
    'Clothesline', 'SevereStrike', 'Inflame', 'BodySlam', 'Carnage',
    # Rare
    'Bludgeon', 'LimitBreak', 'Pummel', 'Uppercut', 'Offering',
]
