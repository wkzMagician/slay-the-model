"""Silent rare skill card - Bullet Time."""

from typing import List

from actions.card import SetCostUntilEndOfTurnAction
from actions.combat import ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from powers.definitions.no_draw import NoDrawPower
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class BulletTime(Card):
    card_type = CardType.SKILL
    rarity = RarityType.RARE

    base_cost = 3
    upgrade_cost = 2

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        from engine.game_state import game_state
        from engine.runtime_api import add_actions

        actions = [SetCostUntilEndOfTurnAction(card=card, cost_until_end_of_turn=0) for card in list(game_state.player.card_manager.get_pile("hand"))]
        actions.append(ApplyPowerAction(NoDrawPower(duration=1, owner=game_state.player), game_state.player))
        add_actions(actions)
