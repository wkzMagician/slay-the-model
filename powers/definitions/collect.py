from actions.card import AddCardAction
from actions.combat_status import RemovePowerAction
from engine.runtime_api import add_action
from powers.base import Power, StackType
from utils.registry import register

@register("power")
class CollectPower(Power):
    name = "Collect"
    description = "At the start of your turn, add Miracle+ to your hand."
    stack_type = StackType.DURATION

    def on_turn_start(self):
        from cards.colorless.miracle import Miracle

        miracle = Miracle()
        miracle.upgrade()
        add_action(AddCardAction(miracle, dest_pile="hand"))
