from cards.watcher._base import *

@register("card")
class SignatureMove(WatcherAttack):
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
        hand = _player().card_manager.get_pile("hand")
        if any(card is not self and getattr(card, "card_type", None) == CardType.ATTACK for card in hand):
            return False, "Signature Move requires no other attacks in hand."
        return True, None
