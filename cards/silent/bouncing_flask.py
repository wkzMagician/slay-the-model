"""Silent uncommon skill card - Bouncing Flask."""

from typing import List
import random

from actions.combat import ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from powers.definitions.poison import PoisonPower
from utils.registry import register
from utils.types import CardType, RarityType, TargetType


@register("card")
class BouncingFlask(Card):
    """Apply Poison to random enemies multiple times."""

    card_type = CardType.SKILL
    rarity = RarityType.UNCOMMON
    target_type = TargetType.ENEMY_ALL

    base_cost = 2
    base_magic = {"hits": 3, "poison": 1}

    upgrade_magic = {"hits": 4, "poison": 1}

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        enemies = [enemy for enemy in targets if enemy.hp > 0]
        if not enemies:
            return
        from engine.runtime_api import add_actions

        actions = []
        for _ in range(self.get_magic_value("hits")):
            target = random.choice(enemies)
            poison = self.get_magic_value("poison")
            actions.append(ApplyPowerAction(PoisonPower(amount=poison, duration=poison, owner=target), target))
        add_actions(actions)
