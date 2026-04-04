from cards.watcher._base import *

@register("card")
class Alpha(WatcherSkill):
    rarity = RarityType.RARE
    base_cost = 1
    base_exhaust = True
    text_name = "Alpha"
    text_description = "Shuffle a Beta into your draw pile. Exhaust."

    def on_play(self, targets: List = []):
        from cards.watcher.beta import Beta

        add_action(AddCardAction(Beta(), dest_pile="draw_pile"))
