"""
Colorless Rare Attack card - Hand of Greed
"""
from engine.runtime_api import add_actions
from actions.reward import AddGoldAction
from cards.base import Card
from utils.registry import register
from utils.types import CardType, RarityType, TargetType


@register("card")
class HandOfGreed(Card):
    """Deal damage, gain gold if kill"""

    card_type = CardType.ATTACK
    rarity = RarityType.RARE
    target_type = TargetType.ENEMY_SELECT

    base_cost = 2
    base_damage = 20
    base_magic = {"gold_on_kill": 20}

    upgrade_damage = 25
    upgrade_magic = {"gold_on_kill": 25}

    def on_fatal(self, damage: int, target=None, source=None, card=None, damage_type: str = "direct"):
        """If this kills enemy, gain gold"""
        if card is not self or target is None:
            return

        actions = []

        gold_amount = self.get_magic_value("gold_on_kill")
        actions.append(AddGoldAction(amount=gold_amount))

        add_actions(actions)