from cards.watcher._base import *

@register("card")
class EmptyBody(WatcherSkill):
    rarity = RarityType.COMMON
    base_cost = 1
    base_block = 7
    upgrade_block = 10
    text_name = "Empty Body"
    text_description = "Gain {block} Block. Exit your stance."

    def on_play(self, targets: List = []):
        super().on_play(targets)
        add_action(ChangeStanceAction(StatusType.NEUTRAL))
