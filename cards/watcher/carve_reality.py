from actions.card import AddCardAction
from cards.base import Card
from engine.runtime_api import add_action
from typing import List
from utils.registry import register
from utils.types import CardType, RarityType, TargetType

@register("card")
class CarveReality(Card):
    card_type = CardType.ATTACK
    target_type = TargetType.ENEMY_SELECT
    rarity = RarityType.UNCOMMON
    base_cost = 1
    base_damage = 6
    upgrade_damage = 10
    text_name = "Carve Reality"
    text_description = "Deal {damage} damage. Add a Smite into your hand."

    def on_play(self, targets: List = []):
        from cards.colorless.smite import Smite

        super().on_play(targets)
        add_action(AddCardAction(Smite(), dest_pile="hand"))
