from actions.card_choice import ChooseCardLambdaAction, MoveCardAction
from actions.combat import EndTurnAction
from actions.watcher import ChangeStanceAction
from cards.base import Card
from engine.runtime_api import add_actions
from typing import List
from utils.registry import register
from utils.types import CardType, RarityType, StatusType, TargetType


@register("card")
class Meditate(Card):
    card_type = CardType.SKILL
    target_type = TargetType.SELF
    rarity = RarityType.UNCOMMON
    base_cost = 1
    base_magic = {"pick": 1}
    upgrade_magic = {"pick": 2}
    base_exhaust = True
    text_name = "Meditate"
    text_description = "Put up to {magic.pick} cards from your discard pile into your hand. Enter Calm. Exhaust."

    def on_play(self, targets: List = []):
        add_actions(
            [
                ChooseCardLambdaAction(
                    pile="discard_pile",
                    amount=self.get_magic_value("pick"),
                    must_select=False,
                    action_builder=lambda card: MoveCardAction(card=card, src_pile="discard_pile", dst_pile="hand"),
                ),
                ChangeStanceAction(StatusType.CALM),
                EndTurnAction(),
            ]
        )
