from actions.card import AddCardAction
from engine.runtime_api import add_action
from powers.base import Power, StackType
from utils.registry import register

@register("power")
class BattleHymnPower(Power):
    name = "Battle Hymn"
    description = "At the start of your turn, add a Smite into your hand."
    stack_type = StackType.PRESENCE

    def on_turn_start(self):
        from cards.colorless.smite import Smite

        add_action(AddCardAction(Smite(), dest_pile="hand"))
