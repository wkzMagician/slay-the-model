from cards.watcher._base import *

@register("card")
class Perseverance(WatcherSkill):
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
        if self in _player().card_manager.get_pile("hand"):
            self._block += self.get_magic_value("retain_gain")
