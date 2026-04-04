from cards.watcher._base import *

@register("card")
class ConjureBlade(WatcherSkill):
    rarity = RarityType.RARE
    base_cost = COST_X
    base_exhaust = True
    text_name = "Conjure Blade"
    text_description = "Shuffle an Expunger into your draw pile. Exhaust."

    def on_play(self, targets: List = []):
        from cards.watcher.expunger import Expunger

        hits = self.get_effective_x() + (1 if self.upgrade_level > 0 else 0)
        add_action(AddCardAction(Expunger(hits=max(1, hits)), dest_pile="draw_pile"))
