"""Hex Power - Causes player to spawn Dazed cards when playing skills."""
from engine.runtime_api import add_action, add_actions
from powers.base import Power, StackType
from utils.registry import register


@register("power")
class HexPower(Power):
    """Hex causes the player to add a Dazed card to their discard pile
    whenever they play a Skill card.
    
    This is a debuff power typically applied by the Chosen enemy.
    """
    
    def __init__(self, amount: int = 1, owner=None):
        super().__init__(amount=amount, owner=owner)
        self.name = "Hex"
        self.is_buff = False
        self.is_debuff = True
        self.stack_type = StackType.INTENSITY
    
    def get_description(self) -> str:
        return f"Whenever you play a Skill, add {self.amount} Dazed card(s) to your discard pile."
    
    def on_card_play(self, card, targets) -> None:
        """Trigger when a card is played - add Dazed if it's a Skill."""
        from utils.types import CardType
        from engine.game_state import game_state
        from cards.colorless import Dazed
        
        if hasattr(card, 'card_type') and card.card_type == CardType.SKILL:
            for _ in range(self.amount):
                dazed = Dazed()
                if game_state and game_state.player:
                    game_state.player.card_manager.piles['discard_pile'].append(dazed)
