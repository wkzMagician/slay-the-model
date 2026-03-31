"""Silent uncommon attack card - Flechettes."""

from typing import List

from actions.combat import AttackAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType, TargetType


@register("card")
class Flechettes(Card):
    """Deal damage once for each Skill in your hand."""

    card_type = CardType.ATTACK
    rarity = RarityType.UNCOMMON
    target_type = TargetType.ENEMY_SELECT

    base_cost = 1
    base_damage = 4

    upgrade_damage = 6

    @property
    def attack_times(self) -> int:
        from engine.game_state import game_state

        player = getattr(game_state, "player", None)
        if player is None:
            return 0
        return sum(
            1
            for card in player.card_manager.get_pile("hand")
            if getattr(card, "card_type", None) == CardType.SKILL
        )

    def on_play(self, targets: List[Creature] = []):
        target = targets[0] if targets else None
        if target is None:
            return
        from engine.runtime_api import add_actions

        from engine.game_state import game_state

        actions = [AttackAction(damage=self.damage, target=target, source=game_state.player, damage_type="attack", card=self) for _ in range(self.attack_times)]
        add_actions(actions)
