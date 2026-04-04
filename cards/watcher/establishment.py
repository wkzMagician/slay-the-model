from cards.watcher._base import *

@register("card")
class Establishment(WatcherPowerCard):
    rarity = RarityType.RARE
    base_cost = 1
    text_name = "Establishment"
    text_description = "At the end of your turn, reduce the cost of retained cards by 1."

    def on_play(self, targets: List = []):
        add_action(ApplyPowerAction(EstablishmentPower(owner=_player()), _player()))
