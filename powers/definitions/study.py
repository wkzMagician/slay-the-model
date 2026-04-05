from actions.card import AddCardAction
from engine.runtime_api import add_action
from powers.base import Power
from utils.registry import register

@register("power")
class StudyPower(Power):
    name = "Study"
    description = "At the end of your turn, shuffle {amount} Insight into your draw pile."

    def on_turn_end(self):
        super().on_turn_end()
        from cards.colorless.insight import Insight

        for _ in range(max(0, self.amount)):
            add_action(AddCardAction(Insight(), dest_pile="draw_pile"))
