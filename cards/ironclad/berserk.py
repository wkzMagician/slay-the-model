"""
Ironclad Rare Power card - Berserk
"""

from typing import List
from actions.base import Action
from actions.combat import ApplyPowerAction, LoseHPAction, GainEnergyAction
from cards.base import Card
from entities.creature import Creature
from utils.dynamic_values import get_magic_value
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Berserk(Card):
    """Gain 2 (1) Vulnerable. At start of your turn, gain 1 Energy."""

    card_type = CardType.POWER
    rarity = RarityType.RARE

    base_cost = 0
    
    base_magic = {"Vulnerable": 2}
    upgrade_magic = {"Vulnerable": 1}

    def on_play(self, target: Creature | None = None) -> List[Action]:
        from engine.game_state import game_state

        actions = super().on_play(target)
        
        magic = get_magic_value(self, "Vulnerable")

        # Apply BerserkPower (which handles energy gain) and VulnerablePower
        actions.append(ApplyPowerAction(power="BerserkPower", target=game_state.player, amount=1, duration=0))
        actions.append(ApplyPowerAction(power="Vulnerable", target=game_state.player, amount=-1, duration=magic))

        return actions
