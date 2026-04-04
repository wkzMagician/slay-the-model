from powers.definitions._watcher_common import *

@register("power")
class BlasphemerPower(Power):
    name = "Blasphemer"
    description = "At the start of your next turn, die."
    stack_type = StackType.PRESENCE

    def __init__(self, amount: int = 0, duration: int = -1, owner=None):
        super().__init__(amount=amount, duration=duration, owner=owner)
        self.armed = True

    def on_turn_start(self):
        if self.owner is None or not self.armed:
            return
        self.armed = False
        add_actions(
            [
                LoseHPAction(amount=self.owner.hp, target=self.owner, source=self),
                RemovePowerAction("Blasphemer", self.owner),
            ]
        )
