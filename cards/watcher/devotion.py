from cards.watcher._base import *

@register("card")
class Devotion(WatcherPowerCard):
    rarity = RarityType.RARE
    base_cost = 1
    base_magic = {"mantra": 2}
    upgrade_magic = {"mantra": 3}
    text_name = "Devotion"
    text_description = "At the start of your turn, gain {magic.mantra} Mantra."

    def on_play(self, targets: List = []):
        add_action(ApplyPowerAction(DevotionPower(amount=self.get_magic_value("mantra"), owner=_player()), _player()))
