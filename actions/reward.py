from engine.runtime_api import add_action, add_actions, publish_message, request_input, set_terminal_state
from typing import List, Optional, TYPE_CHECKING

from tui.print_utils import tui_print
from actions.base import Action
from localization import LocalStr, t
from utils.option import Option
from utils.registry import register, get_registered_instance
from utils.random import get_random_relic, get_random_potion
from utils.types import RarityType

# Use TYPE_CHECKING to avoid circular import
if TYPE_CHECKING:
    from relics.base import Relic


def _handle_obtained_relic(relic: "Relic"):
    from engine.game_state import game_state
    from engine.messages import RelicObtainedMessage

    if not relic or not game_state.player:
        return

    game_state.player.relics.append(relic)
    game_state.obtained_relics.add(relic.idstr)
    tui_print(t("ui.received_relic", default=f"Received relic: {relic.idstr}!", name=relic.local("name")))
    publish_message(
        RelicObtainedMessage(owner=game_state.player, relic=relic),
    )

# Reward actions
@register("action")
class AddRelicAction(Action):
    """Add a specific relic instance to player
    
    Required:
        relic (Relic): Relic instance to add
    """
    def __init__(self, relic: "Relic"):
        self.relic = relic
    
    def execute(self) -> None:
        """Execute: add relic to player"""
        from engine.game_state import game_state
        if self.relic and game_state.player:
            _handle_obtained_relic(self.relic)
            
@register("action")
class AddRelicByNameAction(Action):
    """Add a relic by its idstr/name to player
    
    Required:
        relic_id (str): Relic idstr/name to lookup and add
    """
    def __init__(self, relic_id: str):
        self.relic_id = relic_id
    
    def execute(self) -> None:
        """Execute: lookup relic by name and add to player"""
        from engine.game_state import game_state
        if self.relic_id and game_state.player:
            relic = get_registered_instance("relic", self.relic_id)
            if relic:
                _handle_obtained_relic(relic)
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
        rarities: Optional[List[RarityType]] = None,
        rarity: Optional[RarityType] = None,
        pool: Optional[str] = None,
        characters: Optional[List[str]] = None,
        character: Optional[str] = None,
        exclude_relics: Optional[List[str]] = None,
    ):
        if rarities is not None:
            self.rarities: List[RarityType] = rarities if isinstance(rarities, list) else [rarities]
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
        self.exclude_relics: List[str] = list(exclude_relics or [])
    
    def execute(self) -> None:
        from engine.game_state import game_state
        if game_state.player:
            relic = get_random_relic(
                characters=list(self.characters) if self.characters is not None else None,
                rarities=list(self.rarities),
                exclude=self.exclude_relics,
            )
            if relic:
                _handle_obtained_relic(relic)
            
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
    
    def execute(self) -> None:
        from engine.game_state import game_state
        if not game_state.player:
            return

        if self.relic and self.relic in game_state.player.relics:
            game_state.player.relics.remove(self.relic)
            return

        if self.relic_type is not None:
            for relic in list(game_state.player.relics):
                if isinstance(relic, self.relic_type):
                    game_state.player.relics.remove(relic)
                    break

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
    
    def execute(self) -> None:
        from engine.game_state import game_state
        from relics.base import RarityType
        from actions.display import InputRequestAction
        
        # Generate boss relics (rare tier)
        relics = []
        for _ in range(self.amount):
            relic = get_random_relic(rarities=[RarityType.BOSS])
            if relic:
                relics.append(relic)
        
        if not relics:
            return
        
        # Create selection action
        options = []
        for relic in relics:
            options.append({
                'name': relic.idstr,
                'actions': [AddRelicAction(relic=relic)]
            })
        
        from engine.game_state import game_state
        add_action(
            InputRequestAction(
                title="Choose a boss relic:",
                options=options,
            ),
            to_front=True,
        )

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
    
    def execute(self) -> None:
        import random
        from engine.game_state import game_state
        from engine.messages import GoldGainedMessage
        if game_state.player:
            if random.random() < self.chance:
                # Ectoplasm: block all gold gain.
                if any(getattr(relic, "idstr", None) == "Ectoplasm"
                       for relic in game_state.player.relics):
                    return

                # Calculate modified gold amount through relics
                modified_amount = self.amount
                for relic in game_state.player.relics:
                    hook = getattr(relic, "modify_gold_gained", None)
                    if hook is not None:
                        modified_amount = hook(modified_amount)
                
                game_state.player.gold += modified_amount
                tui_print(t("rewards.gold", default="Gained {amount} gold", amount=modified_amount))
                publish_message(
                    GoldGainedMessage(
                        owner=game_state.player,
                        amount=modified_amount,
                    ),
                )
            else:
                tui_print(t("rewards.gold_fail", default="Failed to gain gold", chance=self.chance))
            
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
    
    def execute(self) -> None:
        from engine.game_state import game_state
        if game_state.player:
            if self.amount == 'all':
                loss = game_state.player.gold
            elif isinstance(self.amount, str):
                try:
                    loss = int(self.amount)
                except ValueError:
                    return
            else:
                loss = self.amount

            game_state.player.gold = max(0, game_state.player.gold - loss)
            
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
    
    def execute(self) -> None:
        potion = get_random_potion(characters=[self.character])
        if potion:
            AddPotionAction(potion=potion).execute()

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
    
    def execute(self) -> None:
        from engine.game_state import game_state
        from actions.display import InputRequestAction
        player = game_state.player
        if not player:
            return
        if self.potion is None:
            return
        # Sozu: player can no longer obtain potions.
        if any(getattr(relic, "idstr", None) == "Sozu" for relic in player.relics):
            return

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
            add_action(
                InputRequestAction(
                    title="ui.potion_full_title",
                    options=options,
                ),
                to_front=True,
            )
            return

        added = player.potions.append(self.potion)
        if added:
            tui_print(t("ui.received_potion", default=f"Received potion: {self.potion.idstr}!", name=self.potion.local("name")))

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

    def execute(self) -> None:
        from engine.game_state import game_state
        if not game_state.player:
            return
        if self.new_potion is None or not isinstance(self.index, int):
            return
        potions = game_state.player.potions
        if 0 <= self.index < len(potions):
            potions[self.index] = self.new_potion
            tui_print(t("ui.received_potion", default=f"Received potion: {self.new_potion.idstr}!", name=self.new_potion.local("name")))
            return


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
    def __init__(self, index: Optional[int] = None, potion = None):
        self.index = index
        self.potion = potion
    
    def execute(self) -> None:
        from engine.game_state import game_state
        if not game_state.player:
            return
        
        if self.index is not None:
            # Remove by index
            if 0 <= self.index < len(game_state.player.potions):
                game_state.player.potions.pop(self.index)
        elif self.potion is not None:
            # Remove by instance
            if self.potion in game_state.player.potions:
                game_state.player.potions.remove(self.potion)
        
