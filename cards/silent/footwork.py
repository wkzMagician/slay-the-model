"""Silent uncommon power card - Footwork."""

from typing import List

from actions.combat import ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Footwork(Card):
    """Gain Dexterity."""

    card_type = CardType.POWER
    rarity = RarityType.UNCOMMON

    base_cost = 1
    base_magic = {"dexterity": 2}

    upgrade_magic = {"dexterity": 3}

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        from engine.game_state import game_state
        from engine.runtime_api import add_actions

        add_actions([
            ApplyPowerAction(power="Dexterity", target=game_state.player, amount=self.get_magic_value("dexterity"))
        ])
