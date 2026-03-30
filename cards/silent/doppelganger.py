"""Silent rare skill card - Doppelganger."""

from typing import List

from actions.combat import ApplyPowerAction
from cards.base import COST_X, Card
from entities.creature import Creature
from powers.definitions.draw_card_next_turn import DrawCardNextTurnPower
from powers.definitions.energized import EnergizedPower
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Doppelganger(Card):
    card_type = CardType.SKILL
    rarity = RarityType.RARE

    base_cost = COST_X
    upgrade_cost = 0

    def on_play(self, targets: List[Creature] = []):
        from engine.game_state import game_state
        from engine.runtime_api import add_actions

        x_value = getattr(self, '_x_cost_energy', 0)
        add_actions([
            ApplyPowerAction(EnergizedPower(amount=x_value, owner=game_state.player), game_state.player),
            ApplyPowerAction(DrawCardNextTurnPower(amount=x_value, owner=game_state.player), game_state.player),
        ])
