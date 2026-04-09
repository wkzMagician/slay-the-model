from actions.combat import GainBlockAction
from engine.runtime_api import add_action
from powers.base import Power
from utils.registry import register
from utils.types import CardType

@register("power")
class TalkToTheHandPower(Power):
    name = "Talk to the Hand"
    description = "Whenever you attack this enemy, gain {amount} Block."
    is_buff = False

    def on_physical_attack_taken(self, damage, source=None, card=None, damage_type="physical"):
        from engine.game_state import game_state

        if damage <= 0 or getattr(card, "card_type", None) != CardType.ATTACK:
            return
        if self.owner is None or game_state.player is None:
            return
        add_action(GainBlockAction(self.amount, target=game_state.player, source=card, card=card))
