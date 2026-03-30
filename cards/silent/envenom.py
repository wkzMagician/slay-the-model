"""Silent rare power card - Envenom."""

from typing import List

from actions.combat import ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from powers.definitions.envenom import EnvenomPower
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Envenom(Card):
    """Attacks apply Poison."""

    card_type = CardType.POWER
    rarity = RarityType.RARE

    base_cost = 2
    base_magic = {"poison": 1}

    upgrade_magic = {"poison": 2}

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        from engine.game_state import game_state
        from engine.runtime_api import add_actions

        add_actions([
            ApplyPowerAction(EnvenomPower(amount=self.get_magic_value("poison"), owner=game_state.player), game_state.player)
        ])
