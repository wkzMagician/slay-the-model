from actions.combat_status import ApplyPowerAction
from cards.base import Card
import engine.game_state as game_state_module
from engine.runtime_api import add_action
from powers.definitions.vulnerable import VulnerablePower
from typing import List
from utils.registry import register
from utils.types import CardType, RarityType, TargetType


@register("card")
class CrushJoints(Card):
    card_type = CardType.ATTACK
    target_type = TargetType.ENEMY_SELECT
    rarity = RarityType.COMMON
    base_cost = 1
    base_damage = 8
    upgrade_damage = 10
    base_magic = {"vuln": 1}
    upgrade_magic = {"vuln": 2}
    text_name = "Crush Joints"
    text_description = "Deal {damage} damage. If the previous card played this turn was a Skill, apply {magic.vuln} Vulnerable."

    def on_play(self, targets: List = []):
        target = targets[0] if targets else None
        super().on_play(targets)
        player = game_state_module.game_state.player
        discard = [] if player is None else player.card_manager.get_pile("discard_pile")
        previous = discard[-1] if discard else None
        if target is None or previous is None or getattr(previous, "card_type", None) != CardType.SKILL:
            return
        amount = self.get_magic_value("vuln")
        add_action(ApplyPowerAction(VulnerablePower(amount=amount, duration=amount, owner=target), target))
