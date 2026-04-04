from cards.watcher._base import *

@register("card")
class Insight(WatcherSkill):
    rarity = RarityType.SPECIAL
    base_cost = 0
    base_draw = 2
    upgrade_draw = 3
    base_retain = True
    base_exhaust = True
    text_name = "Insight"
    text_description = "Retain. Draw {draw} cards. Exhaust."
