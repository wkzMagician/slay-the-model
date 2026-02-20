"""
Ironclad Uncommon Skill card - Rage
"""

from typing import List
from actions.base import Action
from actions.combat import ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Rage(Card):
    """Whenever you play a ATTACK card this turn, gain 3/5 Block"""

    card_type = CardType.SKILL
    rarity = RarityType.UNCOMMON

    base_cost = 0

    base_magic = {"block_per_attack": 3}
    upgrade_magic = {"block_per_attack": 5}

    def on_play(self, targets: List[Creature] = []) -> List[Action]:
        target = targets[0] if targets else None
        from engine.game_state import game_state

        actions = super().on_play(targets)

        # Apply RagePower
        block_per_attack = self.get_magic_value("block_per_attack")
        actions.append(ApplyPowerAction(target=game_state.player, power="RagePower", amount=block_per_attack))

        return actions

    
