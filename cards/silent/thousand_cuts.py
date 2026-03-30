"""Silent rare power card - A Thousand Cuts."""

from typing import List

from actions.combat import ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from powers.definitions.thousand_cuts import ThousandCutsPower
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class ThousandCuts(Card):
    """Whenever you play a card, deal damage to all enemies."""

    card_type = CardType.POWER
    rarity = RarityType.RARE

    base_cost = 2
    base_magic = {"damage": 1}

    upgrade_magic = {"damage": 2}

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        from engine.game_state import game_state
        from engine.runtime_api import add_actions

        add_actions([
            ApplyPowerAction(ThousandCutsPower(amount=self.get_magic_value("damage"), owner=game_state.player), game_state.player)
        ])
