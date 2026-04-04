from cards.watcher._base import *

@register("card")
class Rushdown(WatcherPowerCard):
    rarity = RarityType.UNCOMMON
    base_cost = 1
    base_magic = {"draw": 2}
    text_name = "Rushdown"
    text_description = "Whenever you enter Wrath, draw {magic.draw} cards."

    def on_play(self, targets: List = []):
        add_action(ApplyPowerAction(RushdownPower(amount=self.get_magic_value("draw"), owner=_player()), _player()))
