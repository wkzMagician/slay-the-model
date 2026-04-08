"""
Ironclad Rare Attack card - Fiend Fire
"""
from engine.runtime_api import add_action, add_actions

from typing import List
from actions.base import Action
from actions.card import ExhaustCardAction
from actions.combat import AttackAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class FiendFire(Card):
    """Exhaust all cards in hand, deal damage for each"""

    card_type = CardType.ATTACK
    rarity = RarityType.RARE

    base_cost = 2
    base_exhaust = True
    
    base_magic = {"exhaust_damage": 7}
    upgrade_magic = {"exhaust_damage": 10}

    def on_play(self, targets: List[Creature] = []):
        target = targets[0] if targets else None
        from engine.game_state import game_state

        super().on_play(targets)

        actions = []
        player = game_state.player
        hand = player.card_manager.get_pile('hand')
        assert hand is not None
        cards_in_hand = [card for card in list(hand) if card is not self]

        for card in cards_in_hand:
            actions.append(ExhaustCardAction(card=card, source_pile="hand"))

        damage = self._magic.get("exhaust_damage", 7)
        for _ in cards_in_hand:
            if target and target.hp > 0:
                actions.append(AttackAction(damage=damage, target=target, source=player))

        from engine.game_state import game_state

        add_actions(actions)

        return
