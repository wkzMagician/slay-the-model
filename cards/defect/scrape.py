"""Defect uncommon attack card - Scrape."""

from typing import List

from actions.base import LambdaAction
from actions.card_lifecycle import DiscardCardAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Scrape(Card):
    card_type = CardType.ATTACK
    rarity = RarityType.UNCOMMON

    base_cost = 1
    base_damage = 7
    base_magic = {"draw": 4}
    upgrade_damage = 10
    upgrade_magic = {"draw": 5}

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        from engine.game_state import game_state
        from engine.messages import CardDrawnMessage
        from engine.runtime_api import add_action

        def _draw_and_process_one() -> None:
            player = game_state.player
            if player is None:
                return
            drawn_card = player.card_manager.draw_one()
            if drawn_card is None:
                return
            game_state.publish_message(CardDrawnMessage(card=drawn_card, owner=player))
            if drawn_card.cost != 0:
                add_action(DiscardCardAction(card=drawn_card, source_pile="hand"))

        for _ in range(self.get_magic_value("draw")):
            add_action(LambdaAction(_draw_and_process_one))
