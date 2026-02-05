"""
Coffee Dripper - Uncommon relic
Gain 3 Energy every time you play a Power card.
"""
from relics.base import Relic
from utils.types import RarityType
from utils.registry import register


@register("relic")
class CoffeeDripper(Relic):
    """Coffee Dripper - Gain 3 Energy when playing Power cards"""

    def __init__(self):
        super().__init__()
        self.idstr = "CoffeeDripper"
        self.name_key = "relics.coffee_dripper.name"
        self.description_key = "relics.coffee_dripper.description"
        self.rarity = RarityType.UNCOMMON

    def on_card_played(self, card):
        """Gain 3 Energy when playing a Power card"""
        from utils.types import CardType

        if card.card_type == CardType.POWER:
            from actions.energy import GainEnergyAction

            # Gain 3 energy
            return GainEnergyAction(amount=3)

        return None
