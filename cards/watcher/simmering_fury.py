from actions.combat_status import ApplyPowerAction
from cards.base import Card
import engine.game_state as game_state_module
from engine.runtime_api import add_action
from powers.definitions.simmering_fury_next_turn import SimmeringFuryNextTurnPower
from typing import List
from utils.registry import register
from utils.types import CardType, RarityType, TargetType


@register("card")
class SimmeringFury(Card):
    card_type = CardType.SKILL
    target_type = TargetType.SELF
    rarity = RarityType.UNCOMMON
    base_cost = 1
    base_magic = {"next_draw": 2}
    upgrade_magic = {"next_draw": 3}
    text_name = "Simmering Fury"
    text_description = "Next turn, enter Wrath and draw {magic.next_draw} cards."

    def on_play(self, targets: List = []):
        player = game_state_module.game_state.player
        add_action(
            ApplyPowerAction(
                SimmeringFuryNextTurnPower(amount=self.get_magic_value("next_draw"), owner=player),
                player,
            )
        )
