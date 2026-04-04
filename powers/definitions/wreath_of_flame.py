from powers.definitions._watcher_common import *

@register("power")
class WreathOfFlamePower(Power):
    name = "Wreath of Flame"
    description = "Your next Attack deals {amount} additional damage."
    modify_phase = DamagePhase.ADDITIVE

    def modify_damage_dealt(self, base_damage: int, card=None, target=None) -> int:
        if getattr(card, "card_type", None) == CardType.ATTACK:
            return base_damage + self.amount
        return base_damage

    def on_card_play(self, card, player, targets):
        if getattr(card, "card_type", None) == CardType.ATTACK and self.owner is not None:
            add_action(RemovePowerAction("Wreath of Flame", self.owner))
