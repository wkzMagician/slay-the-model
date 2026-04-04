from cards.watcher._base import *

@register("card")
class DevaForm(WatcherPowerCard):
    rarity = RarityType.RARE
    base_cost = 3
    text_name = "Deva Form"
    text_description = "At the start of your turn, gain Energy and increase this effect."

    def on_play(self, targets: List = []):
        from powers.definitions.deva import DevaPower

        add_action(ApplyPowerAction(DevaPower(duration=1, owner=_player()), _player()))
