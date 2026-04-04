from cards.watcher._base import *

@register("card")
class Collect(WatcherSkill):
    rarity = RarityType.UNCOMMON
    base_cost = COST_X
    base_exhaust = True
    text_name = "Collect"
    text_description = "Put Miracle+ into your hand at the start of your next X turns. Exhaust."

    def on_play(self, targets: List = []):
        duration = self.get_effective_x() + (1 if self.upgrade_level > 0 else 0)
        add_action(ApplyPowerAction(CollectPower(duration=duration, owner=_player()), _player()))
