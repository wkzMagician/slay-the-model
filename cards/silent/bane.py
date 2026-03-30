"""Silent uncommon attack card - Bane."""

from typing import List

from actions.combat import AttackAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Bane(Card):
    """Deal bonus damage to poisoned enemies."""

    card_type = CardType.ATTACK
    rarity = RarityType.UNCOMMON

    base_cost = 1
    base_damage = 7

    upgrade_damage = 10

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        target = targets[0] if targets else None
        if target is None or target.get_power("Poison") is None:
            return

        from engine.game_state import game_state
        from engine.runtime_api import add_actions

        add_actions([
            AttackAction(
                damage=self.damage,
                target=target,
                source=game_state.player,
                damage_type="attack",
                card=self,
            )
        ])
