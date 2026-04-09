"""Defect uncommon attack card - Blizzard."""

from typing import List

from actions.combat import AttackAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, DamageType, RarityType, TargetType


@register("card")
class Blizzard(Card):
    card_type = CardType.ATTACK
    rarity = RarityType.UNCOMMON
    base_target_type = TargetType.ENEMY_ALL

    base_cost = 1
    base_magic = {"per_frost": 2}
    upgrade_magic = {"per_frost": 3}

    @property
    def damage(self) -> int:
        from engine.game_state import game_state

        current_combat = getattr(game_state, "current_combat", None)
        frost_count = 0
        if current_combat is not None:
            frost_count = current_combat.combat_state.orb_history.get("Frost", 0)
        return frost_count * self.get_magic_value("per_frost")

    def on_play(self, targets: List[Creature] = []):
        from engine.game_state import game_state
        from engine.runtime_api import add_action

        for target in targets:
            add_action(AttackAction(damage=self.damage, target=target, source=game_state.player, damage_type=DamageType.PHYSICAL, card=self))
