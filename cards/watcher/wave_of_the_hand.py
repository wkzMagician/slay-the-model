from actions.combat_status import ApplyPowerAction
from cards.base import Card
import engine.game_state as game_state_module
from engine.runtime_api import add_action
from powers.definitions.wave_of_the_hand import WaveOfTheHandPower
from typing import List
from utils.registry import register
from utils.types import CardType, RarityType, TargetType

@register("card")
class WaveOfTheHand(Card):
    card_type = CardType.POWER
    target_type = TargetType.SELF
    rarity = RarityType.UNCOMMON
    base_cost = 1
    base_magic = {"weak": 1}
    upgrade_magic = {"weak": 2}
    text_name = "Wave of the Hand"
    text_description = "Whenever you gain Block this turn, apply {magic.weak} Weak to ALL enemies."

    def on_play(self, targets: List = []):
        add_action(ApplyPowerAction(WaveOfTheHandPower(amount=self.get_magic_value("weak"), duration=1, owner=game_state_module.game_state.player), game_state_module.game_state.player))
