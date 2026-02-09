# Ironclad Potions - Character-specific potions for Ironclad
from typing import List
from actions.base import Action
from actions.card import ExhaustCardAction
from actions.combat import ApplyPowerAction, HealAction
from actions.display import SelectAction
from potions.base import Potion
from utils.types import RarityType
from utils.option import Option
from utils.registry import register

# Common Potions
@register("potion")
class BloodPotion(Potion):
    """Heal 20% max HP (40% with Sacred Bark) - Ironclad only"""
    rarity = RarityType.COMMON
    category = "Ironclad"
    name = "Blood Potion"

    def __init__(self):
        super().__init__()
        self._amount = 20  # Sacred Bark doubles to 40 (percentage)

    def on_use(self, target) -> List[Action]:
        from engine.game_state import game_state
        from actions.combat import HealAction
        # Calculate heal amount as percentage of max HP
        heal_amount = int(game_state.player.max_hp * (self.amount / 100.0))
        return [HealAction(target=game_state.player, amount=heal_amount)]

# Uncommon Potions
@register("potion")
class Elixir(Potion):
    """Exhaust any number of cards from hand - Ironclad only"""
    rarity = RarityType.UNCOMMON
    category = "Ironclad"
    name = "Elixir"

    def __init__(self):
        super().__init__()

    def on_use(self, target) -> List[Action]:
        from actions.card import ExhaustCardAction
        from actions.display import SelectAction
        from engine.game_state import game_state
        from localization import LocalStr
        
        # Build options for each card in hand
        options = []
        for card in list(game_state.player.card_manager.get_pile("hand")):
            options.append(Option(
                name=card.display_name,
                actions=[ExhaustCardAction(card=card, source_pile="hand")]
            ))
        
        # Add a "Done" option
        options.append(Option(
            name=LocalStr("ui.done"),
            actions=[]
        ))
        
        # Let player choose which cards to exhaust (multi-select mode)
        # Use max_select=-1 to allow selecting all hand cards
        return [SelectAction(
            title="Elixir",
            options=options,
            max_select=-1,  # Allow selecting all options
            must_select=False  # Allow stopping selection early
        )]

# Rare Potions
@register("potion")
class HeartOfIron(Potion):
    """Gain 6 Metallicize (12 with Sacred Bark) - Ironclad only"""
    rarity = RarityType.RARE
    category = "Ironclad"
    name = "Heart of Iron"

    def __init__(self):
        super().__init__()
        self._amount = 6  # Sacred Bark doubles to 12

    def on_use(self, target) -> List[Action]:
        from engine.game_state import game_state
        return [ApplyPowerAction(power="Metallicize", target=game_state.player, amount=self.amount)]