from cards.watcher._base import *

@register("card")
class Study(WatcherPowerCard):
    rarity = RarityType.UNCOMMON
    base_cost = 1
    base_magic = {"amount": 2}
    upgrade_magic = {"amount": 3}
    text_name = "Study"
    text_description = "At the end of your turn, shuffle {magic.amount} Insight into your draw pile."

    def on_play(self, targets: List = []):
        from powers.definitions.study import StudyPower

        add_action(ApplyPowerAction(StudyPower(amount=self.get_magic_value("amount"), owner=_player()), _player()))
