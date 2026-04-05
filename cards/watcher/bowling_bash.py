from actions.combat_cards import AttackAction
from cards.base import Card
import engine.game_state as game_state_module
from engine.runtime_api import add_action
from typing import List
from utils.registry import register
from utils.types import CardType, RarityType, TargetType


@register("card")
class BowlingBash(Card):
    card_type = CardType.ATTACK
    target_type = TargetType.ENEMY_SELECT
    rarity = RarityType.COMMON
    base_cost = 1
    base_damage = 7
    upgrade_damage = 10
    text_name = "Bowling Bash"
    text_description = "Deal {damage} damage for each enemy in combat."

    def on_play(self, targets: List = []):
        target = targets[0] if targets else None
        if target is None:
            return
        alive_enemies = [
            enemy for enemy in (game_state_module.game_state.current_combat.enemies if game_state_module.game_state.current_combat else [])
            if not enemy.is_dead()
        ]
        for _ in range(max(1, len(alive_enemies))):
            add_action(AttackAction(self.damage, target=target, source=game_state_module.game_state.player, damage_type="attack", card=self))
