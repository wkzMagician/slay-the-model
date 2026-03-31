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

    @property
    def attack_times(self) -> int:
        from engine.game_state import game_state

        targets = []
        current_combat = getattr(game_state, "current_combat", None)
        if current_combat is not None:
            targets = list(getattr(current_combat.combat_state, "last_card_targets", []))
        target = targets[0] if targets else None
        return 2 if target is not None and target.get_power("Poison") is not None else 1

    def on_play(self, targets: List[Creature] = []):
        current_target = targets[0] if targets else None
        from engine.game_state import game_state

        if game_state.current_combat is not None:
            game_state.current_combat.combat_state.last_card_targets = list(targets)
        if current_target is None:
            return
        super().on_play(targets)
