"""Defect uncommon attack card - Sunder."""

from typing import List

from actions.combat import GainEnergyAction
from actions.combat_cards import AttackAction
from actions.combat_damage import DealDamageAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


class SunderDamageAction(DealDamageAction):
    """Sunder rewards zero HP, including a temporary half-dead collapse."""

    def execute(self) -> None:
        from actions.combat_cleanup import clear_post_combat_actions_if_finished
        from engine.runtime_api import add_action

        # Do not turn an already invalid or cancelled attack into a reward.
        if not self.target or self.target.hp <= 0 or self.should_cancel_source():
            return
        super().execute()
        if self.target.hp <= 0:
            add_action(GainEnergyAction(energy=3))
        # The original SunderAction checks again after adding its reward: a
        # final kill removes this energy action with other post-combat work.
        clear_post_combat_actions_if_finished()


class SunderAttackAction(AttackAction):
    damage_action_type = SunderDamageAction


@register("card")
class Sunder(Card):
    card_type = CardType.ATTACK
    rarity = RarityType.UNCOMMON

    base_cost = 3
    base_damage = 24
    upgrade_damage = 32

    def on_play(self, targets: List[Creature] = []):
        from engine.runtime_api import add_action
        from engine.game_state import game_state
        from utils.dynamic_values import attack_base_damage

        if game_state.player is not None:
            for target in targets:
                add_action(SunderAttackAction(
                    damage=attack_base_damage(self), target=target,
                    source=game_state.player, card=self,
                ))
