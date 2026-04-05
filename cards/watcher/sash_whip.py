from actions.combat_status import ApplyPowerAction
from cards.base import Card
import engine.game_state as game_state_module
from engine.runtime_api import add_action
from powers.definitions.weak import WeakPower
from typing import List
from utils.registry import register
from utils.types import CardType, RarityType, TargetType


@register("card")
class SashWhip(Card):
    card_type = CardType.ATTACK
    target_type = TargetType.ENEMY_SELECT
    rarity = RarityType.COMMON
    base_cost = 1
    base_damage = 8
    upgrade_damage = 10
    base_magic = {"weak": 1}
    upgrade_magic = {"weak": 2}
    text_name = "Sash Whip"
    text_description = "Deal {damage} damage. If the previous card played this turn was an Attack, apply {magic.weak} Weak."

    def on_play(self, targets: List = []):
        target = targets[0] if targets else None
        player = game_state_module.game_state.player
        discard = [] if player is None else player.card_manager.get_pile("discard_pile")
        previous = discard[-1] if discard else None
        super().on_play(targets)
        if target is None or previous is None or getattr(previous, "card_type", None) != CardType.ATTACK:
            return
        amount = self.get_magic_value("weak")
        add_action(ApplyPowerAction(WeakPower(amount=amount, duration=amount, owner=target), target))
