"""
Ironclad Uncommon Attack card - Hemokinesis
"""

from typing import List
from actions.base import Action
from actions.combat import LoseHPAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Hemokinesis(Card):
    """Lose HP, deal damage"""

    card_type = CardType.ATTACK
    rarity = RarityType.UNCOMMON

    base_cost = 1
    base_damage = 15
    base_heal = -2

    upgrade_damage = 20

    def on_play(self, targets: List[Creature] = []):
        from engine.game_state import game_state
        from engine.runtime_api import add_actions
        from actions.combat_cards import AttackAction
        from utils.dynamic_values import attack_base_damage, resolve_card_value

        player = game_state.player
        # Pay HP before attacking. A real death cancels the source's attack;
        # a Fairy/Tail revival allows it to proceed.
        add_actions([
            LoseHPAction(amount=abs(resolve_card_value(self, "heal")),
                         source=player, card=self),
            *[AttackAction(damage=attack_base_damage(self), target=target,
                           source=player, card=self) for target in targets],
        ])
