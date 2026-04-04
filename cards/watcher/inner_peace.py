from cards.watcher._base import *

@register("card")
class InnerPeace(WatcherSkill):
    rarity = RarityType.UNCOMMON
    base_cost = 1
    base_draw = 3
    upgrade_draw = 4
    text_name = "Inner Peace"
    text_description = "Enter Calm. If you are already in Calm, draw {draw} cards."

    def on_play(self, targets: List = []):
        was_calm = _player().status_manager.status == StatusType.CALM
        add_action(ChangeStanceAction(StatusType.CALM))
        if was_calm:
            add_action(DrawCardsAction(self.draw))
