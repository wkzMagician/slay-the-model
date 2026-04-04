from cards.watcher._base import *

@register("card")
class DeusExMachina(WatcherSkill):
    rarity = RarityType.RARE
    base_cost = COST_UNPLAYABLE
    base_exhaust = True
    base_magic = {"count": 2}
    upgrade_magic = {"count": 3}
    text_name = "Deus Ex Machina"
    text_description = "Unplayable. When drawn, add {magic.count} Miracles to your hand. Exhaust."

    def on_draw(self):
        from cards.watcher.miracle import Miracle

        for _ in range(self.get_magic_value("count")):
            add_action(AddCardAction(Miracle(), dest_pile="hand"))
        add_action(ExhaustCardAction(self, source_pile="hand"))
