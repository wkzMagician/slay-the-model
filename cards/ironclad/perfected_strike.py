"""
Ironclad Common Attack card - Perfected Strike
"""

from cards.base import Card
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class PerfectedStrike(Card):
    """Deal damage, plus additional for each Strike card"""

    card_type = CardType.ATTACK
    rarity = RarityType.COMMON

    base_cost = 2
    base_damage = 6
    base_magic = {"strike_damage": 2, "damage_bonus": 2}

    upgrade_damage = 6
    upgrade_magic = {"strike_damage": 3, "damage_bonus": 3}

    @property
    def damage(self) -> int:
        """Damage plus additional for each Strike in deck"""
        from engine.game_state import game_state

        base_damage = self._damage

        deck = game_state.player.card_manager.get_pile('hand')
        draw_pile = game_state.player.card_manager.get_pile('draw_pile')
        discard_pile = game_state.player.card_manager.get_pile('discard_pile')
        # Count Strike cards in hand, draw_pile and discard_pile
        strike_count = sum(1 for card in deck if "Strike" in card.__class__.__name__)
        strike_count += sum(1 for card in draw_pile if "Strike" in card.__class__.__name__)
        strike_count += sum(1 for card in discard_pile if "Strike" in card.__class__.__name__)

        additional_damage = strike_count * self.get_magic_value("strike_damage")

        return base_damage + additional_damage
