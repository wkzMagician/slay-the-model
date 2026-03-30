"""Silent uncommon power card - Noxious Fumes."""

from typing import List

from actions.combat import ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from powers.definitions.noxious_fumes import NoxiousFumesPower
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class NoxiousFumes(Card):
    """Apply Poison to all enemies each turn."""

    card_type = CardType.POWER
    rarity = RarityType.UNCOMMON

    base_cost = 1
    base_magic = {"poison": 2}
    upgrade_magic = {"poison": 3}

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        from engine.game_state import game_state
        from engine.runtime_api import add_actions

        add_actions([
            ApplyPowerAction(
                NoxiousFumesPower(amount=self.get_magic_value("poison"), owner=game_state.player),
                game_state.player,
            )
        ])
