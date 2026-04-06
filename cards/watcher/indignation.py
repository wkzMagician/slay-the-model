from actions.combat_status import ApplyPowerAction
from actions.watcher import ChangeStanceAction
from cards.base import Card
import engine.game_state as game_state_module
from engine.runtime_api import add_action
from powers.definitions.vulnerable import VulnerablePower
from typing import List
from utils.registry import register
from utils.types import CardType, RarityType, StatusType, TargetType


@register("card")
class Indignation(Card):
    card_type = CardType.SKILL
    target_type = TargetType.SELF
    rarity = RarityType.UNCOMMON
    base_cost = 1
    base_magic = {"vuln": 3}
    upgrade_magic = {"vuln": 5}
    text_name = "Indignation"
    text_description = "If you are not in Wrath, enter Wrath. Otherwise, apply {magic.vuln} Vulnerable to ALL enemies."

    def on_play(self, targets: List = []):
        player = game_state_module.game_state.player
        if player.status_manager.status != StatusType.WRATH:
            add_action(ChangeStanceAction(StatusType.WRATH))
            return

        combat = game_state_module.game_state.current_combat
        if combat is None:
            return

        amount = self.get_magic_value("vuln")
        for enemy in list(combat.enemies):
            if enemy.is_dead():
                continue
            add_action(ApplyPowerAction(VulnerablePower(amount=amount, duration=amount, owner=enemy), enemy))
