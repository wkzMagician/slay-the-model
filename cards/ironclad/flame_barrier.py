"""
Ironclad Uncommon Power card - Flame Barrier
"""

from typing import List
from actions.base import Action
from actions.combat import ApplyPowerAction, GainBlockAction
from cards.base import Card
from entities.creature import Creature
from utils.dynamic_values import get_magic_value
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class FlameBarrier(Card):
    """Gain block, deal damage to enemies that attack"""

    card_type = CardType.POWER
    rarity = RarityType.UNCOMMON

    base_cost = 2
    base_block = 12

    upgrade_block = 16
    
    base_magic = {"counter_attack": 4}
    upgrade_magic = {"counter_attack": 6}

    def on_play(self, targets: List[Creature] = []) -> List[Action]:
        target = targets[0] if targets else None
        from engine.game_state import game_state

        actions = super().on_play(targets)

        # Gain block
        actions.append(GainBlockAction(block=self.block, target=game_state.player))

        # Apply FlameBarrierPower (which deals damage when attacked)
        damage_amount = get_magic_value(self, "counter_attack")
        actions.append(ApplyPowerAction(power="FlameBarrierPower", target=game_state.player, amount=damage_amount, duration=1))

        return actions
