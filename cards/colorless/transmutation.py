"""
Colorless Rare Skill card - Transmutation
"""
from engine.runtime_api import add_action, add_actions

from typing import List
from actions.base import Action
from actions.card import AddRandomCardAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Transmutation(Card):
    """Add X random colorless cards, cost X energy, Exhaust"""

    card_type = CardType.SKILL
    rarity = RarityType.RARE

    base_cost = -1  # COST_X
    base_exhaust = True

    def on_play(self, targets: List[Creature] = []):
        from engine.game_state import game_state

        super().on_play(targets)

        actions = []
        # Get X value (energy spent before card play).
        x_value = getattr(self, "_x_cost_energy", 0)
        has_chemical_x = any(
            getattr(relic, "idstr", None) == "ChemicalX"
            for relic in game_state.player.relics
        )
        if has_chemical_x:
            x_value += 2

        # Add X random colorless cards
        use_upgraded = self.upgrade_level > 0

        for _ in range(x_value):
            actions.append(AddRandomCardAction(
                pile="hand",
                namespace="colorless",
                cost_until_end_of_turn=0,  # Cost 0 this turn
                upgrade=use_upgraded  # Add upgrade parameter
            ))

        from engine.game_state import game_state

        add_actions(actions)

        return
