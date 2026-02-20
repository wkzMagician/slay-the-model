from typing import Optional, Union, List, TYPE_CHECKING
from actions.base import LambdaAction
from entities.creature import Creature
from utils.types import TargetType 

if TYPE_CHECKING:
    from cards.base import Card

def resolve_target(target_type: TargetType) -> List[Optional[Creature]]:
    """Resolve target based on TargetType enum
    
    Args:
        target_type: TargetType enum value indicating the type of target to resolve
        show_selection: Whether to show selection UI for human mode (default: True)
        card: Card being played (used to create proper PlayCardBHAction in options)
        ignore_energy: Whether to ignore energy cost
    
    Returns:
        Creature instance or list of Creatures representing the resolved target
        For ENEMY_SELECT with show_selection=True, returns a SelectAction that handles target selection
    """
    from engine.game_state import game_state
    from actions.display import SelectAction
    from utils.option import Option
    from localization import LocalStr
    
    player = game_state.player
    # Access enemies through current_combat, not combat_state
    combat = game_state.current_combat
    enemies = combat.enemies if combat else []

    if target_type == TargetType.SELF:
        return [player]
    elif target_type == TargetType.ENEMY_LOWEST_HP:
        return [min(enemies, key=lambda e: e.hp) if enemies else None]
    elif target_type == TargetType.ENEMY_RANDOM:
        import random
        return [random.choice(enemies) if enemies else None]
    elif target_type == TargetType.ENEMY_ALL:
        return enemies
    elif target_type == TargetType.ENEMY_SELECT:
        alive_enemies = [e for e in enemies]
        
        # If only one enemy or not showing selection, auto-select
        if len(alive_enemies) <= 1:
            return alive_enemies
        
        # Use SelectAction for target selection instead of input()
        options = []
        for idx, enemy in enumerate(alive_enemies):
            options.append(Option(
                name=LocalStr("combat.select_enemy_option", default=f"{enemy.name} (HP: {enemy.hp}/{enemy.max_hp})"),
                actions=[LambdaAction(func=lambda idx=idx: setattr(game_state, 'last_select_idx', idx))]
            ))
        
        return SelectAction(
            title=LocalStr("combat.select_target", default="=== Select Target ==="),
            options=options,
            max_select=1,
            must_select=True
        )
    else:
        raise ValueError(f"Unsupported TargetType: {target_type}")
    
    
