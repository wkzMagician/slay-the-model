from cards.watcher._base import *

@register("card")
class LikeWater(WatcherPowerCard):
    rarity = RarityType.UNCOMMON
    base_cost = 1
    base_magic = {"block": 5}
    upgrade_magic = {"block": 7}
    text_name = "Like Water"
    text_description = "At the end of your turn, if you are in Calm, gain {magic.block} Block."

    def on_play(self, targets: List = []):
        add_action(ApplyPowerAction(LikeWaterPower(amount=self.get_magic_value("block"), owner=_player()), _player()))
