from cards.watcher._base import *

@register("card")
class MasterReality(WatcherPowerCard):
    rarity = RarityType.RARE
    base_cost = 1
    text_name = "Master Reality"
    text_description = "Whenever a card is created during combat, upgrade it."

    def on_play(self, targets: List = []):
        add_action(ApplyPowerAction(MasterRealityPower(owner=_player()), _player()))
