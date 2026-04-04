from cards.watcher._base import *

@register("card")
class Safety(WatcherSkill):
    rarity = RarityType.SPECIAL
    base_cost = 1
    base_block = 12
    upgrade_block = 16
    base_retain = True
    base_exhaust = True
    text_name = "Safety"
    text_description = "Retain. Gain {block} Block. Exhaust."
