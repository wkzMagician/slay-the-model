from cards.watcher._base import *

@register("card")
class Prostrate(WatcherSkill):
    rarity = RarityType.COMMON
    base_cost = 0
    base_block = 4
    upgrade_block = 6
    base_exhaust = True
    text_name = "Prostrate"
    text_description = "Gain {block} Block. Gain 2 Mantra. Exhaust."

    def on_play(self, targets: List = []):
        super().on_play(targets)
        add_action(GainMantraAction(2))
