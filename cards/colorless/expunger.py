from actions.combat_cards import AttackAction
from cards.base import Card, RawLocalStr
from engine.runtime_api import add_action
from typing import List
from utils.dynamic_values import resolve_potential_damage
from utils.registry import register
from utils.types import CardType, DamageType, RarityType, TargetType


@register("card")
class Expunger(Card):
    card_type = CardType.ATTACK
    target_type = TargetType.ENEMY_SELECT
    rarity = RarityType.SPECIAL
    base_cost = 1
    base_damage = 9
    base_exhaust = True
    text_name = "Expunger"
    text_description = "Deal {damage} damage X times. Exhaust."

    def __init__(self, hits: int = 1, **kwargs):
        self.hits = max(1, hits)
        super().__init__(**kwargs)

    def get_combat_description(self, target=None):
        from engine.game_state import game_state

        player = game_state.player
        damage = self.damage
        if player is not None and target is not None:
            damage = resolve_potential_damage(self.damage, player, target, card=self)
        return RawLocalStr(f"Deal {damage} damage {self.hits} times. Exhaust.")

    def on_play(self, targets: List = []):
        from engine.game_state import game_state

        target = targets[0] if targets else None
        if target is None:
            return
        for _ in range(self.hits):
            add_action(AttackAction(self.damage, target=target, source=game_state.player, damage_type=DamageType.PHYSICAL, card=self))
