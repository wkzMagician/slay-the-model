from cards.watcher._base import *

@register("card")
class Brilliance(WatcherAttack):
    rarity = RarityType.RARE
    base_cost = 1
    base_damage = 12
    upgrade_damage = 16
    text_name = "Brilliance"
    text_description = "Deal {damage} damage. Deals more damage for your Mantra."

    def on_play(self, targets: List = []):
        mantra = _player().get_power("Mantra")
        if mantra is not None:
            self._damage += mantra.amount
        super().on_play(targets)
        self._damage = self.base_damage if self.upgrade_level == 0 else self.upgrade_damage
