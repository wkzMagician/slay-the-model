from cards.watcher._base import *

@register("card")
class Evaluate(WatcherSkill):
    rarity = RarityType.COMMON
    base_cost = 1
    base_block = 6
    upgrade_block = 10
    text_name = "Evaluate"
    text_description = "Gain {block} Block. Shuffle an Insight into your draw pile."

    def on_play(self, targets: List = []):
        from cards.watcher.insight import Insight

        super().on_play(targets)
        add_action(AddCardAction(Insight(), dest_pile="draw_pile"))
