"""
Slimed status card.
"""
from cards.base import Card
from utils.types import CardType, RarityType
from utils.registry import register


@register("card")
class Slimed(Card):
    """Slimed. At the end of your turn, take 1 damage and discard this card."""
    
    card_type = CardType.STATUS
    rarity = RarityType.SPECIAL
    base_cost = 1
    base_block = 0
    base_damage = 0
    base_magic = {}
    
    def on_play(self, target=None):
        """Slimed exhausts when played."""
        from engine.game_state import game_state
        # Exhaust this card (move from hand to exhaust pile)
        game_state.player.card_manager.exhaust(self, 'hand')
        return []  # Return empty list of actions