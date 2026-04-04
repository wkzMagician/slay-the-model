from cards.watcher._base import *

@register("card")
class TalkToTheHand(WatcherAttack):
    rarity = RarityType.UNCOMMON
    base_cost = 1
    base_damage = 5
    upgrade_damage = 8
    base_magic = {"block": 2}
    text_name = "Talk to the Hand"
    text_description = "Deal {damage} damage. Apply a debuff that gives you {magic.block} Block whenever you attack that enemy."

    def on_play(self, targets: List = []):
        target = targets[0] if targets else None
        super().on_play(targets)
        if target is not None:
            add_action(ApplyPowerAction(TalkToTheHandPower(amount=self.get_magic_value("block"), owner=target), target))
