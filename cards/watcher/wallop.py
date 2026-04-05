from actions.combat import GainBlockAction
from cards.base import Card
import engine.game_state as game_state_module
from engine.runtime_api import add_action
from typing import List
from utils.dynamic_values import resolve_potential_damage
from utils.registry import register
from utils.types import CardType, RarityType, TargetType

@register("card")
class Wallop(Card):
    card_type = CardType.ATTACK
    target_type = TargetType.ENEMY_SELECT
    rarity = RarityType.UNCOMMON
    base_cost = 2
    base_damage = 9
    upgrade_damage = 12
    text_name = "Wallop"
    text_description = "Deal {damage} damage. Gain Block equal to damage dealt."

    # todo: 通过 on_damage_dealt
    def on_play(self, targets: List = []):
        target = targets[0] if targets else None
        super().on_play(targets)
        if target is not None:
            predicted = resolve_potential_damage(self.damage, game_state_module.game_state.player, target, card=self)
            add_action(GainBlockAction(predicted, target=game_state_module.game_state.player))
