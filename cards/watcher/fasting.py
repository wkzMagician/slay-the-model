from cards.watcher._base import *

@register("card")
class Fasting(WatcherPowerCard):
    rarity = RarityType.UNCOMMON
    base_cost = 2
    base_magic = {"stat": 3}
    upgrade_magic = {"stat": 4}
    text_name = "Fasting"
    text_description = "Gain {magic.stat} Strength and Dexterity. Gain 1 less Energy at the start of each turn."

    def on_play(self, targets: List = []):
        amount = self.get_magic_value("stat")
        player = _player()
        add_actions(
            [
                ApplyPowerAction(StrengthPower(amount=amount, owner=player), player),
                ApplyPowerAction(DexterityPower(amount=amount, owner=player), player),
                ApplyPowerAction(FastingPower(owner=player), player),
            ]
        )
