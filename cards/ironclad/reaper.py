"""
Ironclad Rare Attack card - Reaper
"""

from typing import List
from actions.base import Action
from actions.combat import AttackAction, HealAction, DealDamageAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType, TargetType


@register("card")
class Reaper(Card):
    """Deal damage to ALL enemies, heal for unblocked damage"""

    card_type = CardType.ATTACK
    rarity = RarityType.RARE
    target_type = TargetType.ENEMY_ALL

    base_cost = 2
    base_damage = 4

    upgrade_damage = 5

    def on_play(self, targets: List[Creature] = []) -> List[Action]:
        """Deal damage to ALL enemies"""
        from engine.game_state import game_state

        actions = []
        for enemy in targets:
            if enemy.hp > 0:
                actions.append(DealDamageAction(
                    target=enemy,
                    damage=self.damage,
                    damage_type="attack",
                    card=self,
                ))
        return actions

    def on_damage_dealt(self, damage: int, target: Creature, card: Card, damage_type: str) -> List[Action]:
        """Vampirism: heal player for damage dealt"""
        from engine.game_state import game_state
        from actions.combat import HealAction

        actions = []
        # Heal for damage dealt (vampirism effect)
        heal_amount = damage
        actions.append(HealAction(
            target=game_state.player,
            amount=heal_amount
        ))
        return actions