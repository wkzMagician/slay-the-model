"""After Image power for Silent."""

from actions.combat import GainBlockAction
from powers.base import Power, StackType
from utils.registry import register


@register("power")
class AfterImagePower(Power):
    name = "After Image"
    description = "Whenever you play a card, gain Block."
    stack_type = StackType.INTENSITY
    is_buff = True

    def __init__(self, amount: int = 1, duration: int = -1, owner=None):
        super().__init__(amount=amount, duration=duration, owner=owner)

    def on_card_play(self, card, targets):
        if self.owner is None:
            return
        from engine.runtime_api import add_actions

        add_actions([GainBlockAction(block=self.amount, target=self.owner)])
