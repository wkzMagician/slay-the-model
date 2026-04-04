from cards.watcher._base import *

@register("card")
class WheelKick(WatcherAttack):
    rarity = RarityType.UNCOMMON
    base_cost = 2
    base_damage = 15
    upgrade_damage = 20
    base_draw = 2
    text_name = "Wheel Kick"
    text_description = "Deal {damage} damage. Draw {draw} cards."

    def on_play(self, targets: List = []):
        super().on_play(targets)
        add_action(DrawCardsAction(self.draw))
