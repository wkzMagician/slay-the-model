"""Defect rare attack card - Core Surge."""

from typing import List

from actions.combat import ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from powers.definitions.artifact import ArtifactPower
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class CoreSurge(Card):
    card_type = CardType.ATTACK
    rarity = RarityType.RARE

    base_cost = 1
    base_damage = 11
    base_exhaust = True
    upgrade_damage = 15

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        from engine.game_state import game_state
        from engine.runtime_api import add_action

        add_action(ApplyPowerAction(ArtifactPower(amount=1, owner=game_state.player), game_state.player))
