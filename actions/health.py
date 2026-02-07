"""
Health-related actions.
"""
from typing import Optional
from actions.base import Action
from utils.result_types import BaseResult, NoneResult
from engine.game_state import game_state
from localization import t
from utils.registry import register


@register("action")
class HealAction(Action):
    """Heal the player for a specified amount

    Required:
        amount (int): Amount to heal

    Optional:
        None
    """
    def __init__(self, amount: int):
        self.amount = amount

    def execute(self) -> 'BaseResult':
        if game_state.player:
            old_hp = game_state.player.hp
            game_state.player.hp = min(game_state.player.hp + self.amount, game_state.player.max_hp)
            healed = game_state.player.hp - old_hp
            print(t("ui.healed", default=f"Healed for {healed} HP.", amount=healed))
        return NoneResult()


@register("action")
class LoseHPAction(Action):
    """Deal damage to player

    Required:
        amount (int): Amount to lose

    Optional:
        None
    """
    def __init__(self, amount: int):
        self.amount = amount

    def execute(self) -> 'BaseResult':
        if game_state.player:
            old_hp = game_state.player.hp
            game_state.player.hp -= self.amount
            lost = old_hp - game_state.player.hp
            print(t("ui.lost_hp", default=f"Lost {lost} HP.", amount=lost))
        return NoneResult()


@register("action")
class GainMaxHPAction(Action):
    """Increase player's max HP

    Required:
        amount (int): Amount to increase

    Optional:
        None
    """
    def __init__(self, amount: int):
        self.amount = amount

    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state

        if game_state.player:
            game_state.player.max_hp += self.amount
            # Also heal same amount
            game_state.player.hp += self.amount
            print(t("ui.gained_max_hp", default=f"Max HP increased by {self.amount}!", amount=self.amount))
        return NoneResult()