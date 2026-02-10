"""
Ironclad Uncommon Skill card - Shockwave
"""

from typing import List
from actions.base import Action
from actions.combat import ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Shockwave(Card):
    """Apply Vulnerable and Weak to ALL enemies"""

    card_type = CardType.SKILL
    rarity = RarityType.UNCOMMON

    base_cost = 2
    base_exhaust = True
    
    base_magic = {"vulnerable": 3, "weak": 3}
    upgrade_magic = {"vulnerable": 5, "weak": 5}

    def on_play(self, target: Creature | None = None) -> List[Action]:
        from engine.game_state import game_state

        actions = super().on_play(target)

        vulnerable_amount = self.get_magic_value("vulnerable")
        weak_amount = self.get_magic_value("weak")

        # Apply Vulnerable and Weak to ALL enemies
        if game_state.current_combat:
            for enemy in game_state.current_combat.enemies:
                if enemy.hp > 0:
                    actions.append(ApplyPowerAction(target=enemy, power="Vulnerable", amount=vulnerable_amount))
                    actions.append(ApplyPowerAction(target=enemy, power="Weak", amount=weak_amount))

        return actions
