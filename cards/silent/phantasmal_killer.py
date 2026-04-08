"""Silent rare skill card - Phantasmal Killer."""

from typing import List

from actions.combat import ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from powers.definitions.phantasmal_next_turn import PhantasmalNextTurnPower
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class PhantasmalKiller(Card):
    """Next turn, your attacks deal double damage."""

    card_type = CardType.SKILL
    rarity = RarityType.RARE

    base_cost = 1
    upgrade_cost = 0

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        from engine.game_state import game_state
        from engine.runtime_api import add_actions

        add_actions([
            ApplyPowerAction(PhantasmalNextTurnPower(amount=1, duration=1, owner=game_state.player), game_state.player)
        ])
