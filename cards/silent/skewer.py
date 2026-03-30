"""Silent uncommon attack card - Skewer."""

from typing import List

from actions.combat import AttackAction
from cards.base import COST_X, Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType, TargetType


@register("card")
class Skewer(Card):
    """Deal damage X times."""

    card_type = CardType.ATTACK
    rarity = RarityType.UNCOMMON
    target_type = TargetType.ENEMY_SELECT

    base_cost = COST_X
    base_damage = 3

    upgrade_damage = 4

    def on_play(self, targets: List[Creature] = []):
        target = targets[0] if targets else None
        if target is None:
            return
        from engine.game_state import game_state
        from engine.runtime_api import add_actions

        times = getattr(self, "_x_cost_energy", 0)
        actions = [AttackAction(damage=self.damage, target=target, source=game_state.player, damage_type="attack", card=self) for _ in range(times)]
        add_actions(actions)
