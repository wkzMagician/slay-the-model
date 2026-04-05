from powers.base import Power
from utils.registry import register

@register("power")
class TemporaryDexterityPower(Power):
    name = "Temporary Dexterity"
    description = "Dexterity this turn."

    def on_turn_end(self):
        super().on_turn_end()
        if self.owner is not None:
            dexterity = self.owner.get_power("Dexterity")
            if dexterity is not None:
                dexterity.amount = max(0, dexterity.amount - self.amount)
                if dexterity.amount == 0:
                    self.owner.remove_power("Dexterity")
            self.owner.remove_power("Temporary Dexterity")
