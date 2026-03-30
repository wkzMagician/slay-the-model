"""Silent uncommon power card - Accuracy."""

from typing import List

from actions.combat import ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from powers.definitions.accuracy import AccuracyPower
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Accuracy(Card):
    """Shivs deal more damage."""

    card_type = CardType.POWER
    rarity = RarityType.UNCOMMON

    base_cost = 1
    base_magic = {"damage": 4}
    upgrade_magic = {"damage": 6}

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        from engine.game_state import game_state
        from engine.runtime_api import add_actions

        add_actions([
            ApplyPowerAction(
                AccuracyPower(amount=self.get_magic_value("damage"), owner=game_state.player),
                game_state.player,
            )
        ])
