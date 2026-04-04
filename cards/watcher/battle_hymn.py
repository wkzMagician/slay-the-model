from cards.watcher._base import *

@register("card")
class BattleHymn(WatcherPowerCard):
    rarity = RarityType.UNCOMMON
    base_cost = 1
    text_name = "Battle Hymn"
    text_description = "At the start of your turn, add a Smite into your hand."

    def on_play(self, targets: List = []):
        add_action(ApplyPowerAction(BattleHymnPower(owner=_player()), _player()))
