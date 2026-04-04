from powers.definitions._watcher_common import *

@register("power")
class TalkToTheHandPower(Power):
    name = "Talk to the Hand"
    description = "Whenever you attack this enemy, gain {amount} Block."
    is_buff = False

    def on_damage_taken(self, damage, source=None, card=None, player=None, damage_type="direct"):
        from engine.game_state import game_state

        if damage <= 0 or getattr(card, "card_type", None) != CardType.ATTACK:
            return
        if self.owner is None or game_state.player is None:
            return
        add_action(GainBlockAction(self.amount, target=game_state.player, source=card, card=card))
