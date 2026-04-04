from cards.watcher._base import *

@register("card")
class ThroughViolence(WatcherAttack):
    rarity = RarityType.SPECIAL
    base_cost = 0
    base_damage = 20
    upgrade_damage = 30
    base_retain = True
    base_exhaust = True
    text_name = "Through Violence"
    text_description = "Retain. Deal {damage} damage. Exhaust."
