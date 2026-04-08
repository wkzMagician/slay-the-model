"""Silent rare skill card - Nightmare."""

from typing import List

from actions.card import ChooseCardLambdaAction, SetNightmarePowerAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Nightmare(Card):
    card_type = CardType.SKILL
    rarity = RarityType.RARE

    base_cost = 3
    base_exhaust = True
    upgrade_cost = 2

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        from engine.runtime_api import add_actions

        add_actions([
            ChooseCardLambdaAction(
                pile="hand",
                amount=1,
                title=self.local("name"),
                must_select=True,
                action_builder=lambda card: [SetNightmarePowerAction(card=card)],
            )
        ])
