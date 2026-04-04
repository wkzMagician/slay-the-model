from cards.watcher._base import *

@register("card")
class SandsOfTime(WatcherAttack):
    rarity = RarityType.UNCOMMON
    base_cost = 4
    base_damage = 20
    upgrade_damage = 26
    base_retain = True
    text_name = "Sands of Time"
    text_description = "Retain. Deal {damage} damage. Retaining this card reduces its cost by 1."

    def on_player_turn_end(self):
        if self in _player().card_manager.get_pile("hand") and self._cost > 0:
            self._cost -= 1
