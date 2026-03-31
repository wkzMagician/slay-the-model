"""Defect common attack card - Go for the Eyes."""

from typing import List

from actions.combat import ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from powers.definitions.weak import WeakPower
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class GoForTheEyes(Card):
    card_type = CardType.ATTACK
    rarity = RarityType.COMMON

    base_cost = 0
    base_damage = 3
    base_magic = {"weak": 1}
    upgrade_damage = 4
    upgrade_magic = {"weak": 2}

    @staticmethod
    def _is_attack_intention(intention) -> bool:
        if intention is None:
            return False
        if getattr(intention, "base_damage", None) is not None:
            return True
        if getattr(intention, "hits", None) is not None or getattr(intention, "base_hits", None) is not None:
            return True
        name = str(getattr(intention, "name", "")).lower()
        if "attack" in name:
            return True
        desc = getattr(intention, "description", "")
        desc_text = desc if isinstance(desc, str) else str(desc.resolve())
        return "damage" in desc_text.lower() or "attack" in desc_text.lower()

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        from engine.runtime_api import add_action

        if not targets:
            return
        target = targets[0]
        intention = getattr(target, "current_intention", None)
        if self._is_attack_intention(intention):
            weak = self.get_magic_value("weak")
            add_action(ApplyPowerAction(WeakPower(amount=weak, duration=weak, owner=target), target))
