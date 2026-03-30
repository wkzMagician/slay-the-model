"""Silent uncommon attack card - Sneaky Strike."""

from typing import List

from actions.combat import GainEnergyAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType, TargetType


@register("card")
class SneakyStrike(Card):
    """If you discarded a card this turn, gain energy back."""

    card_type = CardType.ATTACK
    rarity = RarityType.UNCOMMON
    target_type = TargetType.ENEMY_SELECT

    base_cost = 2
    base_damage = 12

    upgrade_damage = 16

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        from engine.game_state import game_state
        from engine.runtime_api import add_actions

        combat = game_state.current_combat
        if combat is None:
            return
        if combat.combat_state.discarded_cards_this_turn > 0:
            add_actions([GainEnergyAction(energy=2)])
