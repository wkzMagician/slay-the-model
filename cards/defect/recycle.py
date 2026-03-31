"""Defect uncommon skill card - Recycle."""

from typing import List

from actions.card import ChooseCardLambdaAction
from actions.card_lifecycle import ExhaustCardAction
from actions.combat import GainEnergyAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Recycle(Card):
    card_type = CardType.SKILL
    rarity = RarityType.UNCOMMON

    base_cost = 1
    upgrade_cost = 0

    def on_play(self, targets: List[Creature] = []):
        from engine.runtime_api import add_action
        from localization import LocalStr

        add_action(
            ChooseCardLambdaAction(
                pile="hand",
                amount=1,
                title=LocalStr("ui.choose_cards_to_exhaust"),
                must_select=True,
                action_builder=lambda card: [GainEnergyAction(energy=max(0, card.cost)), ExhaustCardAction(card=card)],
            )
        )
