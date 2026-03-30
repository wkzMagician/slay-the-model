"""Silent uncommon power card - Caltrops."""

from typing import List

from actions.combat import ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from powers.definitions.thorns import ThornsPower
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Caltrops(Card):
    """When attacked, deal damage back."""

    card_type = CardType.POWER
    rarity = RarityType.UNCOMMON

    base_cost = 1
    base_magic = {"thorns": 3}

    upgrade_magic = {"thorns": 5}

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        from engine.game_state import game_state
        from engine.runtime_api import add_actions

        add_actions([
            ApplyPowerAction(ThornsPower(amount=self.get_magic_value("thorns"), owner=game_state.player), game_state.player)
        ])
