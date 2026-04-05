from cards.base import Card
import engine.game_state as game_state_module
from utils.registry import register
from utils.types import CardType, RarityType, TargetType

@register("card")
class WindmillStrike(Card):
    card_type = CardType.ATTACK
    target_type = TargetType.ENEMY_SELECT
    rarity = RarityType.UNCOMMON
    base_cost = 2
    base_damage = 7
    upgrade_damage = 10
    base_retain = True
    base_magic = {"gain": 4}
    upgrade_magic = {"gain": 5}
    text_name = "Windmill Strike"
    text_description = "Retain. Deal {damage} damage. Retaining this card increases its damage by {magic.gain}."

    def on_player_turn_end(self):
        if self in game_state_module.game_state.player.card_manager.get_pile("hand"):
            self._damage += self.get_magic_value("gain")
