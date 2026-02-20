"""
Colorless Rare Skill card - The Bomb
"""

from typing import List
from actions.base import Action
from cards.base import Card
from entities.creature import Creature
from powers.base import Power
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class TheBomb(Card):
    """Deal damage to all enemies after 3 turns"""

    card_type = CardType.SKILL
    rarity = RarityType.RARE

    base_cost = 2
    base_magic = {"damage": 40, "turns": 3}

    upgrade_magic = {"damage": 50, "turns": 3}

    def on_play(self, targets: List[Creature] = []) -> List[Action]:
        target = targets[0] if targets else None
        from engine.game_state import game_state
        from actions.combat import ApplyPowerAction

        actions = super().on_play(targets)

        # Apply TheBomb power
        damage_amount = self.get_magic_value("damage")
        turns = self.get_magic_value("turns")
        actions.append(ApplyPowerAction(
            power="TheBombPower",
            target=game_state.player,
            amount=damage_amount,
            duration=turns
        ))

        return actions
