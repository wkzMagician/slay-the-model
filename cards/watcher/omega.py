from cards.watcher._base import *

@register("card")
class Omega(WatcherPowerCard):
    rarity = RarityType.SPECIAL
    base_cost = 3
    base_exhaust = True
    text_name = "Omega"
    text_description = "At the end of your turn, deal 50 damage to ALL enemies."

    def on_play(self, targets: List = []):
        add_action(ApplyPowerAction(OmegaPower(amount=50, owner=_player()), _player()))
