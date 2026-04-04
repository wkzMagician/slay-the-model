from cards.watcher._base import *

@register("card")
class MentalFortress(WatcherPowerCard):
    rarity = RarityType.UNCOMMON
    base_cost = 1
    base_magic = {"block": 4}
    upgrade_magic = {"block": 6}
    text_name = "Mental Fortress"
    text_description = "Whenever you change stances, gain {magic.block} Block."

    def on_play(self, targets: List = []):
        add_action(ApplyPowerAction(MentalFortressPower(amount=self.get_magic_value("block"), owner=_player()), _player()))
