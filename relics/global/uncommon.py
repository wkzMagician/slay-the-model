"""
Uncommon Global Relics
Global relics available to all characters at uncommon rarity.
"""
from relics.base import Relic
from utils.types import RarityType
from utils.registry import register


@register("relic")
class HornCleat(Relic):
    """At the start of your 2nd turn, gain 14 Block."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.UNCOMMON

    def on_player_turn_start(self, player, entities):
        """At the start of your 2nd turn, gain 14 Block."""
        from engine.game_state import game_state
        if game_state.combat_state.combat_turn == 2:
            from actions.combat import GainBlockAction
            return [GainBlockAction(block=14)]
        return []