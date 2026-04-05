from actions.combat_status import ApplyPowerAction
from cards.base import Card
import engine.game_state as game_state_module
from engine.runtime_api import add_action
from powers.definitions.devotion import DevotionPower
from typing import List
from utils.registry import register
from utils.types import CardType, RarityType, TargetType

@register("card")
class Devotion(Card):
    card_type = CardType.POWER
    target_type = TargetType.SELF
    rarity = RarityType.RARE
    base_cost = 1
    base_magic = {"mantra": 2}
    upgrade_magic = {"mantra": 3}
    text_name = "Devotion"
    text_description = "At the start of your turn, gain {magic.mantra} Mantra."

    def on_play(self, targets: List = []):
        add_action(ApplyPowerAction(DevotionPower(amount=self.get_magic_value("mantra"), owner=game_state_module.game_state.player), game_state_module.game_state.player))
