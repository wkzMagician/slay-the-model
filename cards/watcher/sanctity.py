from cards.watcher._base import *

@register("card")
class Sanctity(WatcherSkill):
    rarity = RarityType.UNCOMMON
    base_cost = 1
    base_block = 6
    upgrade_block = 9
    text_name = "Sanctity"
    text_description = "Gain {block} Block. If you are in Calm, draw 2 cards."

    def on_play(self, targets: List = []):
        super().on_play(targets)
        if _player().status_manager.status == StatusType.CALM:
            add_action(DrawCardsAction(2))
