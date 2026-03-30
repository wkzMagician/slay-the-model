"""Silent uncommon power card - Well-Laid Plans."""

from typing import List

from actions.combat import ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from powers.definitions.well_laid_plans import WellLaidPlansPower
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class WellLaidPlans(Card):
    card_type = CardType.POWER
    rarity = RarityType.UNCOMMON

    base_cost = 1
    base_magic = {'retain': 1}
    upgrade_magic = {'retain': 2}

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        from engine.game_state import game_state
        from engine.runtime_api import add_actions

        add_actions([ApplyPowerAction(WellLaidPlansPower(amount=self.get_magic_value('retain'), owner=game_state.player), game_state.player)])
