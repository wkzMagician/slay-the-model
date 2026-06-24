"""
Hellraiser power for Ironclad.
Whenever you draw a card containing "Strike", play it against a random enemy.
"""
from engine.runtime_api import add_action
from typing import Any
from powers.base import Power, StackType
from actions.combat_cards import PlayCardAction
from utils.registry import register


@register("power")
class HellraiserPower(Power):
    """Whenever you draw a card containing "Strike" it is played against a random enemy."""

    name = "Hellraiser"
    description = "Whenever you draw a card containing \"Strike\" it is played against a random enemy."
    stack_type = StackType.PRESENCE
    is_buff = True

    def __init__(self, amount: int = 1, duration: int = -1, owner=None):
        """
        Args:
            amount: Not used
            duration: -1 for permanent
        """
        super().__init__(amount=amount, duration=duration, owner=owner)

    def on_card_draw(self, card: Any):
        """Play Strike cards automatically when drawn."""
        from engine.game_state import game_state

        # Check if card name contains "strike" case-insensitive
        # Check class name, idstr, and display_name to catch upgraded versions
        card_name_candidates = []
        
        # Class name (e.g., "Strike", "PommelStrike")
        if hasattr(card, "__class__"):
            card_name_candidates.append(card.__class__.__name__.lower())
        
        # idstr (e.g., "ironclad.Strike")
        if hasattr(card, "idstr"):
            try:
                card_name_candidates.append(str(card.idstr).lower())
            except Exception:
                pass
        
        # display_name
        if hasattr(card, "display_name"):
            try:
                display_name = card.display_name
                # display_name may be a LocalStr, try to resolve
                if hasattr(display_name, "resolve"):
                    display_name = display_name.resolve()
                card_name_candidates.append(str(display_name).lower())
            except Exception:
                pass
        
        # Check if any candidate contains "strike"
        is_strike = any("strike" in name for name in card_name_candidates if name)
        
        if not is_strike:
            return
        
        # Play the card automatically against a random enemy, ignoring energy cost
        # PlayCardAction with is_auto=True will select a random enemy target
        if game_state.player and hasattr(game_state.player, "card_manager"):
            cm = game_state.player.card_manager
            # Ensure card is in hand before playing
            location = cm.get_card_location(card)
            if location != "hand":
                # Card should already be in hand when on_card_draw fires,
                # but if not, try to move it there
                try:
                    cm.move_to(card, "hand", location)
                except Exception:
                    # If we can't move it, skip auto-play
                    return
            
            add_action(PlayCardAction(card=card, is_auto=True, ignore_energy=True))
