from cards.watcher._base import *

@register("card")
class FearNoEvil(WatcherAttack):
    rarity = RarityType.UNCOMMON
    base_cost = 1
    base_damage = 8
    upgrade_damage = 11
    text_name = "Fear No Evil"
    text_description = "Deal {damage} damage. If the enemy intends to attack, gain 2 Energy."

    def on_play(self, targets: List = []):
        target = targets[0] if targets else None
        super().on_play(targets)
        if target is not None and getattr(target, "current_intention", None) is not None:
            if "attack" in getattr(target.current_intention, "name", "").lower():
                add_action(GainEnergyAction(2))
