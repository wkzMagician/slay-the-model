"""Defect rare skill card - Reboot."""

from typing import List

from actions.card import DrawCardsAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Reboot(Card):
    card_type = CardType.SKILL
    rarity = RarityType.RARE

    base_cost = 0
    base_draw = 4
    base_exhaust = True
    upgrade_draw = 6

    def on_play(self, targets: List[Creature] = []):
        import random
        from engine.game_state import game_state
        from engine.runtime_api import add_action
        from actions.base import LambdaAction

        def _reboot():
            card_manager = game_state.player.card_manager
            for pile_name in ("hand", "discard_pile"):
                for card in list(card_manager.get_pile(pile_name)):
                    card_manager.move_to(card, "draw_pile", src=pile_name)
            random.shuffle(card_manager.get_pile("draw_pile"))

        add_action(LambdaAction(_reboot))
        add_action(DrawCardsAction(count=self.draw))
