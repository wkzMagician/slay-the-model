"""
Ironclad Uncommon Power card - Fire Breathing
"""

from typing import List
from actions.base import Action
from actions.combat import ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class FireBreathing(Card):
    """Whenever you draw a status card, deal 7/10 damage to ALL enemies"""

    card_type = CardType.POWER
    rarity = RarityType.UNCOMMON

    base_cost = 1
    base_magic = {"damage_on_status": 7}
    upgrade_magic = {"damage_on_status": 10}

    def on_play(self, target: Creature | None = None) -> List[Action]:
        from engine.game_state import game_state

        actions = super().on_play(target)

        # Apply FireBreathingPower
        damage_on_status = self.get_magic_value("damage_on_status")
        actions.append(ApplyPowerAction(power="FireBreathing", target=game_state.player, amount=damage_on_status, duration=-1))

        return actions
