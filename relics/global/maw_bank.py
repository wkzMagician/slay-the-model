"""
Maw Bank - Boss relic
Gain 10% interest on gold spent in shops.
"""
from relics.base import Relic
from utils.types import RarityType
from utils.registry import register


@register("relic")
class MawBank(Relic):
    """Maw Bank - Gain 10% interest on gold spent in shops"""

    def __init__(self):
        super().__init__()
        self.idstr = "MawBank"
        self.name_key = "relics.maw_bank.name"
        self.description_key = "relics.maw_bank.description"
        self.rarity = RarityType.BOSS

    def on_shop_open(self):
        """Track when shop is opened"""
        # Gold spent is tracked by game_state.gold_spent_in_shop
        # This is tracked in actions/shop.py
        pass

    def on_shop_close(self):
        """Gain 10% interest on gold spent"""
        from engine.game_state import game_state

        # Get gold spent in shop
        gold_spent = getattr(game_state, "gold_spent_in_shop", 0)

        if gold_spent > 0:
            # Calculate 10% interest
            interest = gold_spent // 10

            # Add interest to player gold
            from actions.reward import AddGoldAction
            return AddGoldAction(amount=interest)

        return None
