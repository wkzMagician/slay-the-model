from cards.watcher._base import *

@register("card")
class Tranquility(WatcherSkill):
    rarity = RarityType.COMMON
    base_cost = 1
    upgrade_cost = 0
    base_retain = True
    base_exhaust = True
    text_name = "Tranquility"
    text_description = "Retain. Enter Calm. Exhaust."

    def on_play(self, targets: List = []):
        add_action(ChangeStanceAction(StatusType.CALM))
