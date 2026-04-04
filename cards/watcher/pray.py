from cards.watcher._base import *

@register("card")
class Pray(WatcherSkill):
    rarity = RarityType.UNCOMMON
    base_cost = 1
    base_block = 4
    upgrade_block = 5
    text_name = "Pray"
    text_description = "Gain {block} Block. Gain 3 Mantra."

    def on_play(self, targets: List = []):
        super().on_play(targets)
        add_action(GainMantraAction(3))
