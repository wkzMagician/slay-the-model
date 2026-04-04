from cards.watcher._base import *

@register("card")
class Tantrum(WatcherAttack):
    rarity = RarityType.UNCOMMON
    base_cost = 1
    base_damage = 3
    upgrade_damage = 4
    base_attack_times = 3
    text_name = "Tantrum"
    text_description = "Deal {damage} damage {attack_times} times. Enter Wrath."

    def on_play(self, targets: List = []):
        super().on_play(targets)
        add_action(ChangeStanceAction(StatusType.WRATH))
