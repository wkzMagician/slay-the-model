"""Silent common skill card - Escape Plan."""

from typing import List

from actions.card import DrawCardsAction
from actions.combat import ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from powers.definitions.escape_plan_check import EscapePlanCheckPower
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class EscapePlan(Card):
    """Draw 1 card. If it is a Skill, gain Block."""

    card_type = CardType.SKILL
    rarity = RarityType.COMMON

    base_cost = 0
    base_magic = {"block": 3}

    upgrade_magic = {"block": 5}

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        from engine.game_state import game_state
        from engine.runtime_api import add_actions

        add_actions([
            ApplyPowerAction(EscapePlanCheckPower(amount=self.get_magic_value("block"), owner=game_state.player), game_state.player),
            DrawCardsAction(count=1),
        ])
