from actions.combat_status import ApplyPowerAction
from actions.display import InputRequestAction
from cards.base import Card, RawLocalStr
import engine.game_state as game_state_module
from engine.runtime_api import add_action
from powers.definitions.plated_armor import PlatedArmorPower
from powers.definitions.strength import StrengthPower
from typing import List
from utils.option import Option
from utils.registry import register
from utils.types import CardType, RarityType, TargetType

@register("card")
class Wish(Card):
    card_type = CardType.SKILL
    target_type = TargetType.SELF
    rarity = RarityType.RARE
    base_cost = 3
    base_exhaust = True
    text_name = "Wish"
    text_description = "Choose one: Gain Gold, Strength, or Plated Armor. Exhaust."

    def on_play(self, targets: List = []):
        from actions.base import LambdaAction

        player = game_state_module.game_state.player
        options = [
            Option(name=RawLocalStr("Gain Gold"), actions=[LambdaAction(lambda: setattr(player, "gold", player.gold + (30 if self.upgrade_level > 0 else 25)))]),
            Option(name=RawLocalStr("Gain Strength"), actions=[ApplyPowerAction(StrengthPower(amount=4 if self.upgrade_level > 0 else 3, owner=player), player)]),
            Option(name=RawLocalStr("Gain Plated Armor"), actions=[ApplyPowerAction(PlatedArmorPower(amount=8 if self.upgrade_level > 0 else 6, owner=player), player)]),
        ]
        add_action(InputRequestAction(title=RawLocalStr("Choose a wish"), options=options))
