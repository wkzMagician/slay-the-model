"""Defect Echo Form power."""

from powers.base import Power, StackType
from utils.registry import register


@register("power")
class EchoFormPower(Power):
    name = "Echo Form"
    description = "The first card you play each turn is played twice."
    stack_type = StackType.INTENSITY
    is_buff = True

    def __init__(self, amount: int = 1, duration: int = -1, owner=None):
        super().__init__(amount=amount, duration=duration, owner=owner)
        self.cards_doubled_this_turn = 0

    def on_turn_start(self):
        self.cards_doubled_this_turn = 0

    def on_card_play(self, card, targets):
        if getattr(card, "_is_replay", False) or self.amount <= 0:
            return
        from engine.game_state import game_state

        combat = game_state.current_combat
        if combat is None:
            return
        # The shared play protocol increments this count before its use hooks.
        # A direct hook call with no recorded play still represents card one.
        played = max(1, combat.combat_state.turn_cards_played)
        if played - self.cards_doubled_this_turn > self.amount:
            return
        from actions.autoplay import queue_replay
        queue_replay(card)
        self.cards_doubled_this_turn += 1
