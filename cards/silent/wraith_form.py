"""Silent rare power card - Wraith Form."""

from typing import List

from actions.combat import ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from powers.definitions.dexterity_down import DexterityDownPower
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class WraithForm(Card):
    """Gain Intangible and lose Dexterity each turn. Exhaust."""

    card_type = CardType.POWER
    rarity = RarityType.RARE

    base_cost = 3
    base_exhaust = True
    base_magic = {"intangible": 2, "dex_down": 1}

    upgrade_magic = {"intangible": 3, "dex_down": 1}

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        from engine.game_state import game_state
        from engine.runtime_api import add_actions

        intangible = self.get_magic_value("intangible")
        add_actions([
            ApplyPowerAction(power="Intangible", target=game_state.player, amount=intangible, duration=intangible),
            ApplyPowerAction(DexterityDownPower(amount=self.get_magic_value("dex_down"), owner=game_state.player), game_state.player),
        ])
