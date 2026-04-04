from cards.watcher._base import *

@register("card")
class EmptyFist(WatcherAttack):
    rarity = RarityType.COMMON
    base_cost = 1
    base_damage = 9
    upgrade_damage = 14
    text_name = "Empty Fist"
    text_description = "Deal {damage} damage. Exit your stance."

    def on_play(self, targets: List = []):
        super().on_play(targets)
        add_action(ChangeStanceAction(StatusType.NEUTRAL))
