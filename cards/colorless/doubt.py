"""
Colorless Curse card - Doubt
"""
from engine.runtime_api import add_action, add_actions

from typing import List
from actions.base import Action, LambdaAction
from actions.combat import ApplyPowerAction
from cards.base import Card, COST_UNPLAYABLE
from powers.definitions.weak import WeakPower
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Doubt(Card):
    """Unplayable, gain 1 Weak at end of turn"""

    card_type = CardType.CURSE
    rarity = RarityType.CURSE

    base_cost = COST_UNPLAYABLE
    upgradeable = False

    def on_player_turn_end(self):
        from actions.card_play_lifecycle import queue_turn_end_card
        queue_turn_end_card(self, LambdaAction(self._resolve_turn_end))

    def _resolve_turn_end(self):
        """Gain 1 Weak at end of turn"""
        from engine.game_state import game_state

        super().on_player_turn_end()

        actions = []
        weak_amount = 1
        actions.append(ApplyPowerAction(
            WeakPower(amount=weak_amount, duration=weak_amount, owner=game_state.player),
            game_state.player
        ))

        from engine.game_state import game_state

        add_actions(actions)

        return
