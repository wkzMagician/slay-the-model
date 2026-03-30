"""Silent rare attack card - Glass Knife."""

from typing import List

from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType, TargetType


@register("card")
class GlassKnife(Card):
    """Deal two heavy hits and lose damage each use."""

    card_type = CardType.ATTACK
    rarity = RarityType.RARE
    target_type = TargetType.ENEMY_SELECT

    base_cost = 1
    base_damage = 8
    base_attack_times = 2
    base_magic = {"decay": 2}

    upgrade_damage = 12

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        self._damage = max(0, self._damage - self.get_magic_value("decay"))
