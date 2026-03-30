"""Silent rare power card - After Image."""

from typing import List

from actions.combat import ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from powers.definitions.after_image import AfterImagePower
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class AfterImage(Card):
    """Gain block whenever you play a card."""

    card_type = CardType.POWER
    rarity = RarityType.RARE

    base_cost = 1
    base_magic = {"block": 1}

    upgrade_cost = 0

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        from engine.game_state import game_state
        from engine.runtime_api import add_actions

        add_actions([
            ApplyPowerAction(AfterImagePower(amount=self.get_magic_value("block"), owner=game_state.player), game_state.player)
        ])
