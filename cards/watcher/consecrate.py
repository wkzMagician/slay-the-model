from cards.watcher._base import *

@register("card")
class Consecrate(WatcherAttack):
    rarity = RarityType.COMMON
    target_type = TargetType.ENEMY_ALL
    base_cost = 0
    base_damage = 5
    upgrade_damage = 8
    text_name = "Consecrate"
    text_description = "Deal {damage} damage to ALL enemies."
