from cards.watcher._base import *

@register("card")
class Worship(WatcherSkill):
    rarity = RarityType.UNCOMMON
    base_cost = 2
    upgrade_cost = 1
    text_name = "Worship"
    text_description = "Gain 5 Mantra."

    def on_play(self, targets: List = []):
        add_action(GainMantraAction(5))
