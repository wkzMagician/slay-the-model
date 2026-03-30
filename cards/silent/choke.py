"""Silent uncommon attack card - Choke."""

from typing import List

from actions.combat import ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from powers.definitions.choke import ChokePower
from utils.registry import register
from utils.types import CardType, RarityType, TargetType


@register("card")
class Choke(Card):
    """Deal damage and punish further card plays this turn."""

    card_type = CardType.ATTACK
    rarity = RarityType.UNCOMMON
    target_type = TargetType.ENEMY_SELECT

    base_cost = 2
    base_damage = 12
    base_magic = {"followup": 3}

    upgrade_damage = 16
    upgrade_magic = {"followup": 5}

    def on_play(self, targets: List[Creature] = []):
        target = targets[0] if targets else None
        super().on_play(targets)
        if target is None:
            return
        from engine.runtime_api import add_actions

        add_actions([
            ApplyPowerAction(ChokePower(amount=self.get_magic_value("followup"), duration=1, owner=target), target)
        ])
