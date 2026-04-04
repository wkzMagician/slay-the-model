from cards.watcher._base import *

@register("card")
class Miracle(WatcherSkill):
    rarity = RarityType.SPECIAL
    base_cost = 0
    base_energy_gain = 1
    upgrade_energy_gain = 2
    base_exhaust = True
    text_name = "Miracle"
    text_description = "Gain {energy_gain} Energy. Exhaust."
