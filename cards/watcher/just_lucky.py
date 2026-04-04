from cards.watcher._base import *

@register("card")
class JustLucky(WatcherAttack):
    rarity = RarityType.COMMON
    base_cost = 0
    base_damage = 3
    upgrade_damage = 4
    base_block = 2
    upgrade_block = 3
    text_name = "Just Lucky"
    text_description = "Deal {damage} damage. Scry 1. Gain {block} Block."

    def on_play(self, targets: List = []):
        super().on_play(targets)
        add_action(ScryAction(1))
