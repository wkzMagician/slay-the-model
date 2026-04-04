from cards.watcher._base import *

@register("card")
class WreathOfFlame(WatcherSkill):
    rarity = RarityType.UNCOMMON
    base_cost = 1
    base_magic = {"bonus": 5}
    upgrade_magic = {"bonus": 8}
    text_name = "Wreath of Flame"
    text_description = "Your next Attack deals {magic.bonus} additional damage."

    def on_play(self, targets: List = []):
        add_action(ApplyPowerAction(WreathOfFlamePower(amount=self.get_magic_value("bonus"), owner=_player()), _player()))
