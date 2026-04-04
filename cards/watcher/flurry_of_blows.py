from cards.watcher._base import *

@register("card")
class FlurryOfBlows(WatcherAttack):
    rarity = RarityType.COMMON
    base_cost = 0
    base_damage = 4
    upgrade_damage = 6
    text_name = "Flurry of Blows"
    text_description = "Deal {damage} damage. Whenever you change stances, return this from your discard pile to your hand."

    @subscribe(StanceChangedMessage, priority=MessagePriority.CARD)
    def on_stance_changed(self, previous_status, new_status):
        add_action(ReturnCardToHandAction(self))
