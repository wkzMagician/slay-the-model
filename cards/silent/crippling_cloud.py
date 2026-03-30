"""Silent uncommon skill card - Crippling Cloud."""

from typing import List

from actions.combat import ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from powers.definitions.poison import PoisonPower
from powers.definitions.weak import WeakPower
from utils.registry import register
from utils.types import CardType, RarityType, TargetType


@register("card")
class CripplingCloud(Card):
    """Apply Weak and Poison to all enemies. Exhaust."""

    card_type = CardType.SKILL
    rarity = RarityType.UNCOMMON
    target_type = TargetType.ENEMY_ALL

    base_cost = 2
    base_exhaust = True
    base_magic = {"weak": 2, "poison": 4}

    upgrade_magic = {"weak": 2, "poison": 7}

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        from engine.runtime_api import add_actions

        actions = []
        weak = self.get_magic_value("weak")
        poison = self.get_magic_value("poison")
        for enemy in targets:
            if enemy.hp <= 0:
                continue
            actions.append(ApplyPowerAction(WeakPower(amount=weak, duration=weak, owner=enemy), enemy))
            actions.append(ApplyPowerAction(PoisonPower(amount=poison, duration=poison, owner=enemy), enemy))
        add_actions(actions)
