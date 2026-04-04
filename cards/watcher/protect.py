from cards.watcher._base import *

@register("card")
class Protect(WatcherSkill):
    rarity = RarityType.COMMON
    base_cost = 2
    upgrade_cost = 1
    base_block = 12
    upgrade_block = 16
    base_retain = True
    text_name = "Protect"
    text_description = "Retain. Gain {block} Block."
