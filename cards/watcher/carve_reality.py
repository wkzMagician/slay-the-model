from cards.watcher._base import *

@register("card")
class CarveReality(WatcherAttack):
    rarity = RarityType.UNCOMMON
    base_cost = 1
    base_damage = 6
    upgrade_damage = 10
    text_name = "Carve Reality"
    text_description = "Deal {damage} damage. Add a Smite into your hand."

    def on_play(self, targets: List = []):
        from cards.watcher.smite import Smite

        super().on_play(targets)
        add_action(AddCardAction(Smite(), dest_pile="hand"))
