from typing import List, Optional, TYPE_CHECKING

from actions.base import Action
from utils.result_types import BaseResult, NoneResult, SingleActionResult, MultipleActionsResult
from localization import LocalStr, t
from utils.option import Option
from utils.registry import register, get_registered_instance
from utils.random import get_random_relic, get_random_potion
from utils.types import RarityType

# Use TYPE_CHECKING to avoid circular import
if TYPE_CHECKING:
    from relics.base import Relic

# Reward actions
@register("action")
class AddRelicAction(Action):
    """Add a specific relic to player
    
    Required:
        relic (str): Relic name
    """
    def __init__(self, relic):
        self.relic = relic
    
    def execute(self) -> BaseResult:
        """Execute: add relic to player"""
        from engine.game_state import game_state
        if self.relic and game_state.player:
            relic = get_registered_instance("relic", self.relic)
            if relic:
                game_state.player.relics.append(relic)
                # Track relic as obtained (even if removed later)
                game_state.obtained_relics.add(relic.idstr)
                print(t("ui.received_relic", default=f"Received relic: {relic.idstr}!", name=relic.idstr))
        return NoneResult()
            
@register("action")
class AddRandomRelicAction(Action):
    """Add a random relic to player
    
    Required:
        rarities (List[RarityType]): Relic rarity
        
    Optional:
        None
    """
    def __init__(self, rarities: List[RarityType]):
        self.rarities = rarities
    
    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state
        if self.rarities and game_state.player:
            relic = get_random_relic(rarities=self.rarities)
            if relic:
                game_state.player.relics.append(relic)
                # Track relic as obtained (even if removed later)
                game_state.obtained_relics.add(relic.idstr)
                print(t("ui.received_relic", default=f"Received relic: {relic.idstr}!", name=relic.idstr))
        return NoneResult()
            
@register("action")
class LoseRelicAction(Action):
    """Lose a specific relic from player
    
    Required:
        relic (Relic): Relic instance to lose
        
    Optional:
        None
    """
    def __init__(self, relic: "Relic"):
        self.relic = relic
    
    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state
        if self.relic and game_state.player:
            game_state.player.relics.remove(self.relic)
        return NoneResult()
            
@register("action")
class AddGoldAction(Action):
    """Add gold to player
    
    Required:
        amount (int): Amount of gold to add
        
    Optional:
        None
    """
    def __init__(self, amount: int):
        self.amount = amount
    
    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state
        if game_state.player:
            game_state.player.gold += self.amount
            print(t("rewards.gold", default="Gained {amount} gold", amount=self.amount))
        return NoneResult()
            
@register("action")
class LoseGoldAction(Action):
    """Lose gold from player
    
    Required:
        amount (int): Amount of gold to lose
        
    Optional:
        None
    """
    def __init__(self, amount: int):
        self.amount = amount
    
    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state
        if game_state.player:
            game_state.player.gold -= self.amount
        return NoneResult()
            
@register("action")
class AddRandomPotionAction(Action):
    """Add a random potion to player
    
    Required:
        character (str): Player character
        
    Optional:
        None
    """
    def __init__(self, character: str):
        self.character = character
    
    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state
        from actions.display import SelectAction
        if game_state.player:
            potion = get_random_potion(characters=[self.character])
            if potion:
                if len(game_state.player.potions) >= game_state.player.potion_limit:
                    options = [
                        Option(name=LocalStr("ui.skip_potion_option"), actions=[]),
                    ]
                    for index, existing in enumerate(game_state.player.potions):
                        options.append(
                            Option(
                                name=LocalStr("ui.replace_potion_option", name=existing.name),
                                actions=[ReplacePotionAction(index=index, new_potion=potion)],
                            )
                        )
                    return SingleActionResult(
                        SelectAction(
                            title="ui.potion_full_title",
                            options=options,
                        )
                    )
                added = game_state.player.potions.append(potion)
                if added:
                    print(t("ui.received_potion", default=f"Received potion: {potion.idstr}!", name=potion.idstr))
        return NoneResult()

@register("action")
class AddPotionAction(Action):
    """Add a potion to player
    
    Required:
        potion: potion instance
        
    Optional:
        None
    """
    def __init__(self, potion):
        self.potion = potion
    
    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state
        added = game_state.player.potions.append(self.potion)
        if added:
            print(t("ui.received_potion", default=f"Received potion: {self.potion.idstr}!", name=self.potion.idstr))
        return NoneResult()

@register("action")
class ReplacePotionAction(Action):
    """Replace a potion at a specific index with a new potion.

    Required:
        index (int): Index of potion to replace
        new_potion (object): Potion instance to place

    Optional:
        None
    """
    def __init__(self, index: int, new_potion):
        self.index = index
        self.new_potion = new_potion

    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state
        if not game_state.player:
            return NoneResult()
        if self.new_potion is None or not isinstance(self.index, int):
            return NoneResult()
        potions = game_state.player.potions
        if 0 <= self.index < len(potions):
            potions[self.index] = self.new_potion
            print(t("ui.received_potion", default=f"Received potion: {self.new_potion.idstr}!", name=self.new_potion.idstr))
            return SingleActionResult(self.new_potion)
        return NoneResult()
