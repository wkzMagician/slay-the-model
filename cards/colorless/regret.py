"""
Colorless Curse card - Regret
"""
from engine.runtime_api import add_action, add_actions

from typing import List
from actions.base import Action, LambdaAction
from actions.combat import LoseHPAction
from cards.base import Card, COST_UNPLAYABLE
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Regret(Card):
    """Unplayable, lose 1 HP for each card in hand at end of turn"""

    card_type = CardType.CURSE
    rarity = RarityType.CURSE

    base_cost = COST_UNPLAYABLE
    upgradeable = False

    def on_player_turn_end(self):
        from actions.card_play_lifecycle import queue_turn_end_card
        queue_turn_end_card(self, LambdaAction(self._resolve_turn_end))

    def _resolve_turn_end(self):
        """Lose 1 HP for each card in hand"""
        from engine.game_state import game_state

        super().on_player_turn_end()

        actions = []
        if game_state.player and hasattr(game_state.player, "card_manager"):
            hand_cards = list(game_state.player.card_manager.get_pile("hand"))
            damage_amount = 1 * len(hand_cards)

            if damage_amount > 0:
                actions.append(LoseHPAction(amount=damage_amount))

        from engine.game_state import game_state

        add_actions(actions)

        return
