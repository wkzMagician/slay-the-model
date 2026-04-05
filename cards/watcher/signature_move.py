from cards.base import Card
import engine.game_state as game_state_module
from utils.registry import register
from utils.types import CardType, RarityType, TargetType

@register("card")
class SignatureMove(Card):
    card_type = CardType.ATTACK
    target_type = TargetType.ENEMY_SELECT
    rarity = RarityType.UNCOMMON
    base_cost = 2
    base_damage = 30
    upgrade_damage = 40
    text_name = "Signature Move"
    text_description = "Can only be played if this is the only Attack in your hand. Deal {damage} damage."

    def can_play(self, ignore_energy=False):
        can_play, reason = super().can_play(ignore_energy)
        if not can_play:
            return can_play, reason
        hand = game_state_module.game_state.player.card_manager.get_pile("hand")
        if any(card is not self and getattr(card, "card_type", None) == CardType.ATTACK for card in hand):
            return False, "Signature Move requires no other attacks in hand."
        return True, None
