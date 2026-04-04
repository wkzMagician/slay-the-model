from cards.watcher._base import *

@register("card")
class Smite(WatcherAttack):
    rarity = RarityType.SPECIAL
    base_cost = 1
    base_damage = 12
    upgrade_damage = 16
    base_retain = True
    base_exhaust = True
    text_name = "Smite"
    text_description = "Retain. Deal {damage} damage. Exhaust."
