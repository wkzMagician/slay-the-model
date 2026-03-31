"""Defect rare skill card - Amplify."""

from typing import List

from actions.combat import ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from powers.definitions.amplify import AmplifyPower
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Amplify(Card):
    card_type = CardType.SKILL
    rarity = RarityType.RARE

    base_cost = 1
    base_magic = {"copies": 1}
    upgrade_magic = {"copies": 2}

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        from engine.game_state import game_state
        from engine.runtime_api import add_action

        add_action(ApplyPowerAction(AmplifyPower(amount=self.get_magic_value("copies"), owner=game_state.player), game_state.player))
