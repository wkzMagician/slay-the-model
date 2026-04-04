from cards.watcher._base import *

@register("card")
class SimmeringFury(WatcherSkill):
    rarity = RarityType.UNCOMMON
    base_cost = 1
    base_magic = {"next_draw": 2}
    upgrade_magic = {"next_draw": 3}
    text_name = "Simmering Fury"
    text_description = "Enter Wrath. Next turn, draw {magic.next_draw} cards."

    def on_play(self, targets: List = []):
        player = _player()
        add_actions(
            [
                ChangeStanceAction(StatusType.WRATH),
                ApplyPowerAction(DrawCardNextTurnPower(amount=self.get_magic_value("next_draw"), duration=1, owner=player), player),
            ]
        )
