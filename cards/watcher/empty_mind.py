from cards.watcher._base import *

@register("card")
class EmptyMind(WatcherSkill):
    rarity = RarityType.UNCOMMON
    base_cost = 1
    base_draw = 2
    upgrade_draw = 3
    text_name = "Empty Mind"
    text_description = "Exit your stance. Draw {draw} cards."

    def on_play(self, targets: List = []):
        add_actions([ChangeStanceAction(StatusType.NEUTRAL), DrawCardsAction(self.draw)])
