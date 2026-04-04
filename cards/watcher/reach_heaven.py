from cards.watcher._base import *

@register("card")
class ReachHeaven(WatcherAttack):
    rarity = RarityType.UNCOMMON
    base_cost = 2
    base_damage = 10
    upgrade_damage = 15
    text_name = "Reach Heaven"
    text_description = "Deal {damage} damage. Shuffle a Through Violence into your draw pile."

    def on_play(self, targets: List = []):
        from cards.watcher.through_violence import ThroughViolence

        super().on_play(targets)
        add_action(AddCardAction(ThroughViolence(), dest_pile="draw_pile"))
