from cards.watcher._base import *

@register("card")
class Halt(WatcherSkill):
    rarity = RarityType.COMMON
    base_cost = 0
    base_block = 3
    upgrade_block = 4
    base_magic = {"wrath_block": 9}
    upgrade_magic = {"wrath_block": 14}
    text_name = "Halt"
    text_description = "Gain {block} Block. If you are in Wrath, gain {magic.wrath_block} more."

    def on_play(self, targets: List = []):
        super().on_play(targets)
        if _player().status_manager.status == StatusType.WRATH:
            add_action(GainBlockAction(self.get_magic_value("wrath_block"), target=_player()))
