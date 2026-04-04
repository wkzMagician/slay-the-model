from cards.watcher._base import *

@register("card")
class Conclude(WatcherAttack):
    rarity = RarityType.UNCOMMON
    target_type = TargetType.ENEMY_ALL
    base_cost = 1
    base_damage = 12
    upgrade_damage = 16
    text_name = "Conclude"
    text_description = "Deal {damage} damage to ALL enemies. End your turn."

    def on_play(self, targets: List = []):
        super().on_play(targets)
        add_action(EndTurnAction())
