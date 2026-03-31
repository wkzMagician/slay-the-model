"""Defect rare power card - Hello World."""

from typing import List

from actions.combat import ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from powers.definitions.hello_world import HelloWorldPower
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class HelloWorld(Card):
    card_type = CardType.POWER
    rarity = RarityType.UNCOMMON

    base_cost = 1
    upgrade_innate = True

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        from engine.game_state import game_state
        from engine.runtime_api import add_action

        add_action(ApplyPowerAction(HelloWorldPower(owner=game_state.player), game_state.player))

