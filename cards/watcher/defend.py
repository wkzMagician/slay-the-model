from cards.watcher._base import *

@register("card")
class Defend(WatcherSkill):
    rarity = RarityType.STARTER
    base_cost = 1
    base_block = 5
    upgrade_block = 8
    text_name = "Defend"
    text_description = "Gain {block} Block."
