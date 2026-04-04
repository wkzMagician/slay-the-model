from powers.definitions._watcher_common import *

@register("power")
class BattleHymnPower(Power):
    name = "Battle Hymn"
    description = "At the start of your turn, add a Smite into your hand."
    stack_type = StackType.PRESENCE

    def on_turn_start(self):
        from cards.watcher import Smite

        add_action(AddCardAction(Smite(), dest_pile="hand"))
