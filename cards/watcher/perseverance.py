from cards.base import Card
import engine.game_state as game_state_module
from utils.registry import register
from utils.types import CardType, RarityType, TargetType

@register("card")
class Perseverance(Card):
    card_type = CardType.SKILL
    target_type = TargetType.SELF
    rarity = RarityType.UNCOMMON
    base_cost = 1
    base_block = 5
    upgrade_block = 7
    base_magic = {"retain_gain": 2}
    upgrade_magic = {"retain_gain": 3}
    base_retain = True
    text_name = "Perseverance"
    text_description = "Retain. Gain {block} Block. When retained, this gains {magic.retain_gain} Block."

    def on_player_turn_end(self):
        if self in game_state_module.game_state.player.card_manager.get_pile("hand"):
            self._block += self.get_magic_value("retain_gain")
