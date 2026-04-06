from actions.card import DrawCardsAction
from actions.combat_status import RemovePowerAction
from actions.watcher import ChangeStanceAction
from engine.runtime_api import add_actions
from powers.base import Power, StackType
from utils.registry import register
from utils.types import StatusType


@register("power")
class SimmeringFuryNextTurnPower(Power):
    name = "Simmering Fury Next Turn"
    description = "Next turn, enter Wrath and draw cards."
    stack_type = StackType.INTENSITY

    def on_turn_start(self):
        if self.owner is None:
            return
        add_actions(
            [
                ChangeStanceAction(StatusType.WRATH),
                DrawCardsAction(self.amount),
                RemovePowerAction(self.name, self.owner),
            ]
        )
