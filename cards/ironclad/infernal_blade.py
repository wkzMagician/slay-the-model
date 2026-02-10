"""
Ironclad Uncommon Skill card - Infernal Blade
"""

from typing import List
from actions.base import Action
from actions.card import ChooseAddRandomCardAction
from actions.combat import ApplyPowerAction, GainBlockAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class InfernalBlade(Card):
    """Choose one of three random Attack card to add to hand. cost 0 this turn."""

    card_type = CardType.SKILL
    rarity = RarityType.UNCOMMON

    base_cost = 1
    base_exhaust = True

    upgrade_cost = 0

    def on_play(self, target: Creature | None = None) -> List[Action]:
        from engine.game_state import game_state

        namespace = game_state.player.namespace

        return super().on_play(target) + [ChooseAddRandomCardAction(namespace=namespace, card_type=CardType.ATTACK, temp_cost=0)]
