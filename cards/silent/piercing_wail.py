"""Silent uncommon skill card - Piercing Wail."""

from typing import List

from actions.combat import ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from powers.definitions.strength import StrengthPower
from powers.definitions.strength_down import StrengthDownPower
from utils.registry import register
from utils.types import CardType, RarityType, TargetType


@register("card")
class PiercingWail(Card):
    """All enemies lose Strength this turn. Exhaust."""

    card_type = CardType.SKILL
    rarity = RarityType.UNCOMMON
    target_type = TargetType.ENEMY_ALL

    base_cost = 1
    base_exhaust = True
    base_magic = {"strength_loss": 6}

    upgrade_magic = {"strength_loss": 8}

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        from engine.runtime_api import add_actions

        actions = []
        strength_loss = self.get_magic_value("strength_loss")
        for enemy in targets:
            if enemy.hp <= 0:
                continue
            actions.append(ApplyPowerAction(StrengthPower(amount=-strength_loss, owner=enemy), enemy))
            actions.append(ApplyPowerAction(StrengthDownPower(amount=strength_loss, duration=1, owner=enemy), enemy))
        add_actions(actions)
