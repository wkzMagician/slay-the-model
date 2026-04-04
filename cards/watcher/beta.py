from cards.watcher._base import *

@register("card")
class Beta(WatcherSkill):
    rarity = RarityType.SPECIAL
    base_cost = 2
    base_exhaust = True
    text_name = "Beta"
    text_description = "Shuffle an Omega into your draw pile. Exhaust."

    def on_play(self, targets: List = []):
        from cards.watcher.omega import Omega

        add_action(AddCardAction(Omega(), dest_pile="draw_pile"))
