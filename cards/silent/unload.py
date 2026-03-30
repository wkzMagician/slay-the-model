"""Silent uncommon attack card - Unload."""

from typing import List

from actions.card import DiscardCardAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType, TargetType


@register("card")
class Unload(Card):
    card_type = CardType.ATTACK
    rarity = RarityType.UNCOMMON
    target_type = TargetType.ENEMY_SELECT

    base_cost = 1
    base_damage = 14

    upgrade_damage = 18

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        from engine.game_state import game_state
        from engine.runtime_api import add_actions

        hand = list(game_state.player.card_manager.get_pile('hand'))
        add_actions([DiscardCardAction(card=card, source_pile='hand') for card in hand])
