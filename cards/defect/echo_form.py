"""Defect rare power card - Echo Form."""

from typing import List

from actions.combat import ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from powers.definitions.echo_form import EchoFormPower
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class EchoForm(Card):
    card_type = CardType.POWER
    rarity = RarityType.RARE

    base_cost = 3
    base_ethereal = True
    upgrade_ethereal = False

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        from engine.game_state import game_state
        from engine.runtime_api import add_action

        add_action(ApplyPowerAction(EchoFormPower(amount=1, owner=game_state.player), game_state.player))
