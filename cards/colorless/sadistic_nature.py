"""
Colorless Rare Power card - Sadistic Nature
"""

from typing import List
from actions.base import Action
from cards.base import Card
from entities.creature import Creature
from powers.base import Power
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class SadisticNature(Card):
    """Power: Deal damage when applying debuff"""

    card_type = CardType.POWER
    rarity = RarityType.RARE

    base_cost = 0
    base_magic = {"damage_on_debuff": 5}

    upgrade_magic = {"damage_on_debuff": 7}

    def on_play(self, targets: List[Creature] = []) -> List[Action]:
        target = targets[0] if targets else None
        from engine.game_state import game_state
        from actions.combat import ApplyPowerAction

        actions = super().on_play(targets)

        # Apply Sadistic Nature power
        damage_amount = self.get_magic_value("damage_on_debuff")
        actions.append(ApplyPowerAction(
            power="SadisticNaturePower",
            target=game_state.player,
            amount=damage_amount,
            duration=-1  # Permanent for this combat
        ))

        return actions
