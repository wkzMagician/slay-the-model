from cards.watcher._base import *

@register("card")
class Blasphemy(WatcherSkill):
    rarity = RarityType.RARE
    base_cost = 1
    base_exhaust = True
    text_name = "Blasphemy"
    text_description = "Enter Divinity. Die next turn. Exhaust."

    def on_play(self, targets: List = []):
        player = _player()
        add_actions([ChangeStanceAction(StatusType.DIVINITY), ApplyPowerAction(BlasphemerPower(owner=player), player)])
