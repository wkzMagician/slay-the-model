from actions.combat_status import ApplyPowerAction
from actions.watcher import TriggerMarkAction
from cards.base import Card
import engine.game_state as game_state_module
from engine.runtime_api import add_action
from powers.definitions.mark import MarkPower
from typing import List
from utils.registry import register
from utils.types import CardType, RarityType, TargetType

@register("card")
class PressurePoints(Card):
    card_type = CardType.SKILL
    target_type = TargetType.SELF
    rarity = RarityType.COMMON
    target_type = TargetType.ENEMY_SELECT
    base_cost = 1
    base_magic = {"mark": 8}
    upgrade_magic = {"mark": 11}
    text_name = "Pressure Points"
    text_description = "Apply {magic.mark} Mark. ALL enemies lose HP equal to their Mark."

    def on_play(self, targets: List = []):
        target = targets[0] if targets else None
        if target is None:
            return
        add_action(ApplyPowerAction(MarkPower(amount=self.get_magic_value("mark"), owner=target), target))
        for enemy in [enemy for enemy in (game_state_module.game_state.current_combat.enemies if game_state_module.game_state.current_combat else []) if not enemy.is_dead()]:
            add_action(TriggerMarkAction(enemy))
