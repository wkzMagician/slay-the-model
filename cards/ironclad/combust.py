"""
Ironclad Uncommon Power card - Combust
"""

from typing import List
from actions.base import Action
from actions.combat import ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Combust(Card):
    """At end of turn, deal 5/7 damage to all enemy"""

    card_type = CardType.POWER
    rarity = RarityType.UNCOMMON

    base_cost = 1
    base_magic = {"combust_damage": 5}
    upgrade_magic = {"combust_damage": 7}

    def on_play(self, target: Creature | None = None) -> List[Action]:
        from engine.game_state import game_state

        actions = super().on_play(target)

        # Apply CombustPower
        combust_damage = self.get_magic_value("combust_damage")
        actions.append(ApplyPowerAction(power="CombustPower", target=game_state.player, amount=combust_damage, duration=0))

        return actions
