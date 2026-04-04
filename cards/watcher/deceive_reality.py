from cards.watcher._base import *

@register("card")
class DeceiveReality(WatcherSkill):
    rarity = RarityType.UNCOMMON
    base_cost = 1
    base_block = 4
    upgrade_block = 7
    text_name = "Deceive Reality"
    text_description = "Gain {block} Block. Add a Safety into your hand."

    def on_play(self, targets: List = []):
        from cards.watcher.safety import Safety

        super().on_play(targets)
        add_action(AddCardAction(Safety(), dest_pile="hand"))
