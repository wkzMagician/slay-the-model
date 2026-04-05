from actions.combat_status import ApplyPowerAction
from cards.base import Card
import engine.game_state as game_state_module
from engine.runtime_api import add_action
from powers.definitions.battle_hymn import BattleHymnPower
from typing import List
from utils.registry import register
from utils.types import CardType, RarityType, TargetType

@register("card")
class BattleHymn(Card):
    card_type = CardType.POWER
    target_type = TargetType.SELF
    rarity = RarityType.UNCOMMON
    base_cost = 1
    text_name = "Battle Hymn"
    text_description = "At the start of your turn, add a Smite into your hand."

    def on_play(self, targets: List = []):
        add_action(ApplyPowerAction(BattleHymnPower(owner=game_state_module.game_state.player), game_state_module.game_state.player))
