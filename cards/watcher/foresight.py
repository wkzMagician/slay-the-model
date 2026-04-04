from cards.watcher._base import *

@register("card")
class Foresight(WatcherPowerCard):
    rarity = RarityType.UNCOMMON
    base_cost = 1
    base_magic = {"scry": 3}
    upgrade_magic = {"scry": 4}
    text_name = "Foresight"
    text_description = "At the start of your turn, Scry {magic.scry}."

    def on_play(self, targets: List = []):
        add_action(ApplyPowerAction(ForesightPower(amount=self.get_magic_value("scry"), owner=_player()), _player()))
