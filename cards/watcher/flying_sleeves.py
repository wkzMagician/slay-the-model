from cards.watcher._base import *

@register("card")
class FlyingSleeves(WatcherAttack):
    rarity = RarityType.COMMON
    base_cost = 1
    base_damage = 4
    upgrade_damage = 6
    base_attack_times = 2
    base_retain = True
    text_name = "Flying Sleeves"
    text_description = "Retain. Deal {damage} damage {attack_times} times."
