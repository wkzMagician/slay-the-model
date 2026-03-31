"""Silent uncommon attack card - Predator."""

from typing import List

from actions.combat import ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from powers.definitions.draw_card_next_turn import DrawCardNextTurnPower
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Predator(Card):
    """Deal heavy damage and draw next turn."""

    card_type = CardType.ATTACK
    rarity = RarityType.UNCOMMON

    base_cost = 2
    base_damage = 15
    base_magic = {"draw_next_turn": 2}

    upgrade_damage = 20

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        from engine.game_state import game_state
        from engine.runtime_api import add_actions

        add_actions([
            ApplyPowerAction(DrawCardNextTurnPower(amount=self.get_magic_value("draw_next_turn"), owner=game_state.player), game_state.player)
        ])
