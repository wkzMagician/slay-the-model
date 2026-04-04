from cards.watcher._base import *

@register("card")
class ThirdEye(WatcherSkill):
    rarity = RarityType.COMMON
    base_cost = 1
    base_block = 7
    upgrade_block = 9
    base_magic = {"scry": 3}
    upgrade_magic = {"scry": 5}
    text_name = "Third Eye"
    text_description = "Gain {block} Block. Scry {magic.scry}."

    def on_play(self, targets: List = []):
        super().on_play(targets)
        add_action(ScryAction(self.get_magic_value("scry")))
