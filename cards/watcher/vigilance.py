from cards.watcher._base import *

@register("card")
class Vigilance(WatcherSkill):
    rarity = RarityType.STARTER
    base_cost = 2
    base_block = 8
    upgrade_block = 12
    text_name = "Vigilance"
    text_description = "Gain {block} Block. Enter Calm."

    def on_play(self, targets: List = []):
        super().on_play(targets)
        add_action(ChangeStanceAction(StatusType.CALM))
