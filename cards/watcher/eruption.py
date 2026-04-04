from cards.watcher._base import *

@register("card")
class Eruption(WatcherAttack):
    rarity = RarityType.STARTER
    base_cost = 2
    upgrade_cost = 1
    base_damage = 9
    upgrade_damage = 12
    text_name = "Eruption"
    text_description = "Deal {damage} damage. Enter Wrath."

    def on_play(self, targets: List = []):
        super().on_play(targets)
        add_action(ChangeStanceAction(StatusType.WRATH))
