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

    # todo: 效果错误：加的是Miracle+
    def on_turn_start(self):
        from cards.colorless.miracle import Miracle

        if self.duration == 0:
            return
        miracle = Miracle()
        miracle.upgrade()
        add_action(AddCardAction(miracle, dest_pile="hand"))
        # todo: 逻辑错误。duration 在每回合结束时会自动-1
        if self.duration > 0:
            self.duration -= 1
            if self.duration == 0 and self.owner is not None:
                add_action(RemovePowerAction("Collect", self.owner))
