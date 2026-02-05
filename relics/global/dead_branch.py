"""
Dead Branch - Boss relic
At the start of your turn, draw 1 card and play a random card from discard pile, then exhaust it.
"""
from relics.base import Relic
from utils.types import RarityType
from utils.registry import register


@register("relic")
class DeadBranch(Relic):
    """Dead Branch - Draw 1 card and play random from discard, then exhaust"""

    def __init__(self):
        super().__init__()
        self.idstr = "DeadBranch"
        self.name_key = "relics.dead_branch.name"
        self.description_key = "relics.dead_branch.description"
        self.rarity = RarityType.BOSS

    def on_turn_start(self):
        """At start of turn, draw and play random card from discard"""
        from actions.card import DrawCardsAction
        from actions.card import PlayCardAction
        from actions.card import ExhaustCardAction

        # Draw 1 card first
        draw_action = DrawCardsAction(count=1)

        # Play random card action (placeholder)
        # In a full implementation, this would select from discard
        # For now, return just draw action
        return draw_action
