"""Silent uncommon skill card - Blur."""

from typing import List

from actions.combat import ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from powers.definitions.blur import BlurPower
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Blur(Card):
    """Gain Block and keep it for one extra turn."""

    card_type = CardType.SKILL
    rarity = RarityType.UNCOMMON

    base_cost = 1
    base_block = 5

    upgrade_block = 8

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        from engine.game_state import game_state
        from engine.runtime_api import add_actions

        add_actions([
            ApplyPowerAction(BlurPower(duration=2, owner=game_state.player), game_state.player)
        ])
