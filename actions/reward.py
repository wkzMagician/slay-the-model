from typing import List, Optional, TYPE_CHECKING

from tui.print_utils import tui_print
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
    """Add a specific relic instance to player
    
    Required:
        relic (Relic): Relic instance to add
    """
    def __init__(self, relic: "Relic"):
        self.relic = relic
    
    def execute(self) -> BaseResult:
        """Execute: add relic to player"""
        from engine.game_state import game_state
        if self.relic and game_state.player:
            game_state.player.relics.append(self.relic)
            # Track relic as obtained (even if removed later)
            game_state.obtained_relics.add(self.relic.idstr)
            tui_print(t("ui.received_relic", default=f"Received relic: {self.relic.idstr}!", name=self.relic.idstr))
            # Trigger on_obtain hook so relic-specific pickup effects fire (e.g., Astrolabe, Orrery, Tiny House)
            if hasattr(self.relic, "on_obtain"):
                actions = self.relic.on_obtain()
                if actions:
                    for action in actions:
                        game_state.action_queue.add_action(action)
        return NoneResult()
            
@register("action")
class AddRelicByNameAction(Action):
    """Add a relic by its idstr/name to player
    
    Required:
        relic_id (str): Relic idstr/name to lookup and add
    """
    def __init__(self, relic_id: str):
        self.relic_id = relic_id
    
    def execute(self) -> BaseResult:
        """Execute: lookup relic by name and add to player"""
        from engine.game_state import game_state
        if self.relic_id and game_state.player:
            relic = get_registered_instance("relic", self.relic_id)
            if relic:
                game_state.player.relics.append(relic)
                # Track relic as obtained (even if removed later)
                game_state.obtained_relics.add(relic.idstr)
                tui_print(t("ui.received_relic", default=f"Received relic: {relic.idstr}!", name=relic.idstr))
                # Trigger on_obtain hook so relic-specific pickup effects fire (e.g., Astrolabe, Orrery)
                if hasattr(relic, "on_obtain"):
                    actions = relic.on_obtain()
                    if actions:
                        for action in actions:
                            game_state.action_queue.add_action(action)
        return NoneResult()
@register("action")
class AddRandomRelicAction(Action):
    """Add a random relic to player
    
    Required:
        rarities (List[RarityType]): Relic rarity (optional, defaults to all rarities)
        
    Optional:
        rarity (RarityType): Single rarity (will be converted to list)
        pool (str): Pool name for special relic pools (e.g., 'face')
    """
    def __init__(
        self,
        rarities: List[RarityType] = None,
        rarity: RarityType = None,
        pool: str = None,
        characters: Optional[List[str]] = None,
        character: Optional[str] = None,
        exclude_relics: Optional[List[str]] = None,
    ):
        if rarities is not None:
            self.rarities = rarities if isinstance(rarities, list) else [rarities]
        elif rarity is not None:
            self.rarities = [rarity]
        else:
            # Default to all rarities
            from relics.base import RarityType as RT
            self.rarities = [RT.COMMON, RT.UNCOMMON, RT.RARE]
        self.pool = pool
        if characters is not None:
            self.characters = (
                characters if isinstance(characters, list) else [characters]
            )
        elif character is not None:
            self.characters = [character]
        else:
            self.characters = None
        self.exclude_relics = exclude_relics or []
    
    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state
        if game_state.player:
            relic = get_random_relic(
                characters=self.characters,
                rarities=self.rarities,
                exclude=self.exclude_relics,
            )
            if relic:
                game_state.player.relics.append(relic)
                # Track relic as obtained (even if removed later)
                game_state.obtained_relics.add(relic.idstr)
                tui_print(t("ui.received_relic", default=f"Received relic: {relic.idstr}!", name=relic.idstr))
        return NoneResult()
            
@register("action")
class LoseRelicAction(Action):
    """Lose a specific relic from player
    
    Required:
        relic (Relic): Relic instance to lose
        
    Optional:
        None
    """
    def __init__(
        self,
        relic: Optional["Relic"] = None,
        relic_type: Optional[type] = None,
    ):
        self.relic = relic
        self.relic_type = relic_type
    
    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state
        if not game_state.player:
            return NoneResult()

        if self.relic and self.relic in game_state.player.relics:
            game_state.player.relics.remove(self.relic)
            return NoneResult()

        if self.relic_type is not None:
            for relic in list(game_state.player.relics):
                if isinstance(relic, self.relic_type):
                    game_state.player.relics.remove(relic)
                    break
        return NoneResult()

@register("action")
class ChooseBossRelicAction(Action):
    """Let player choose from a selection of boss relics
    
    Required:
        None
        
    Optional:
        amount (int): Number of relics to choose from. Default is 3.
    """
    def __init__(self, amount: int = 3):
        self.amount = amount
    
    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state
        from relics.base import RarityType
        from actions.display import SelectAction
        
        # Generate boss relics (rare tier)
        relics = []
        for _ in range(self.amount):
            relic = get_random_relic(rarities=[RarityType.BOSS])
            if relic:
                relics.append(relic)
        
        if not relics:
            return NoneResult()
        
        # Create selection action
        options = []
        for relic in relics:
            options.append({
                'name': relic.idstr,
                'actions': [AddRelicAction(relic=relic)]
            })
        
        return SingleActionResult(SelectAction(
            title="Choose a boss relic:",
            options=options
        ))

@register("action")            
class AddGoldAction(Action):
    """Add gold to player
    
    Required:
        amount (int): Amount of gold to add
        
    Optional:
        chance (float): Probability of adding gold (0.0-1.0). Default is 1.0 (always)
    """
    def __init__(self, amount: int, chance: float = 1.0):
        self.amount = amount
        self.chance = chance
    
    def execute(self) -> 'BaseResult':
        import random
        from engine.game_state import game_state
        if game_state.player:
            if random.random() < self.chance:
                # Ectoplasm: block all gold gain.
                if any(relic.idstr == "Ectoplasm"
                       for relic in game_state.player.relics):
                    return NoneResult()

                # Calculate modified gold amount through relics
                modified_amount = self.amount
                for relic in game_state.player.relics:
                    modified_amount = relic.modify_gold_gained(modified_amount)
                
                game_state.player.gold += modified_amount
                tui_print(t("rewards.gold", default="Gained {amount} gold", amount=modified_amount))
                
                # Trigger on_gold_gained for relics like BloodyIdol
                for relic in game_state.player.relics:
                    actions = relic.on_gold_gained(modified_amount, game_state.player)
                    for action in actions:
                        action.execute()
            else:
                tui_print(t("rewards.gold_fail", default="Failed to gain gold", chance=self.chance))
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
            if self.amount == 'all':
                loss = game_state.player.gold
            elif isinstance(self.amount, str):
                try:
                    loss = int(self.amount)
                except ValueError:
                    return NoneResult()
            else:
                loss = self.amount

            game_state.player.gold = max(0, game_state.player.gold - loss)
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
        potion = get_random_potion(characters=[self.character])
        if potion:
            return AddPotionAction(potion=potion).execute()
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
        from actions.display import SelectAction
        player = game_state.player
        if not player:
            return NoneResult()
        if self.potion is None:
            return NoneResult()
        # Sozu: player can no longer obtain potions.
        if any(getattr(relic, "idstr", None) == "Sozu" for relic in player.relics):
            return NoneResult()

        if len(player.potions) >= player.potion_limit:
            options = [
                Option(name=LocalStr("ui.skip_potion_option"), actions=[]),
            ]
            for index, existing in enumerate(player.potions):
                options.append(
                    Option(
                        name=LocalStr(
                            "ui.replace_potion_option",
                            name=existing.local("name"),
                        ),
                        actions=[
                            ReplacePotionAction(
                                index=index,
                                new_potion=self.potion,
                            )
                        ],
                    )
                )
            return SingleActionResult(
                SelectAction(
                    title="ui.potion_full_title",
                    options=options,
                )
            )

        added = player.potions.append(self.potion)
        if added:
            tui_print(t("ui.received_potion", default=f"Received potion: {self.potion.idstr}!", name=self.potion.idstr))
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
            tui_print(t("ui.received_potion", default=f"Received potion: {self.new_potion.idstr}!", name=self.new_potion.idstr))
            return NoneResult()
        return NoneResult()


@register("action")
class LosePotionAction(Action):
    """Lose a potion from player
    
    Required:
        index (int): Index of potion to lose
        OR
        potion: Potion instance to lose
        
    Optional:
        None
    """
    def __init__(self, index: int = None, potion = None):
        self.index = index
        self.potion = potion
    
    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state
        if not game_state.player:
            return NoneResult()
        
        if self.index is not None:
            # Remove by index
            if 0 <= self.index < len(game_state.player.potions):
                game_state.player.potions.pop(self.index)
        elif self.potion is not None:
            # Remove by instance
            if self.potion in game_state.player.potions:
                game_state.player.potions.remove(self.potion)
        
        return NoneResult()
