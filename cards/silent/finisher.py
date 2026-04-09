"""Silent uncommon attack card - Finisher."""

from typing import List

from actions.combat import AttackAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, DamageType, RarityType, TargetType


@register("card")
class Finisher(Card):
    """Deal damage once for each Attack played this turn."""

    card_type = CardType.ATTACK
    rarity = RarityType.UNCOMMON
    target_type = TargetType.ENEMY_SELECT

    base_cost = 1
    base_damage = 6

    upgrade_damage = 8

    @property
    def attack_times(self) -> int:
        from engine.game_state import game_state

        combat = getattr(game_state, "current_combat", None)
        if combat is None:
            return 0
        return combat.combat_state.turn_attack_cards_played

    def on_play(self, targets: List[Creature] = []):
        target = targets[0] if targets else None
        if target is None:
            return
        from engine.game_state import game_state
        from engine.runtime_api import add_actions

        actions = [AttackAction(damage=self.damage, target=target, source=game_state.player, damage_type=DamageType.PHYSICAL, card=self) for _ in range(self.attack_times)]
        add_actions(actions)
