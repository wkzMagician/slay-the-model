from typing import Optional, Union, List, TYPE_CHECKING
from entities.creature import Creature
from utils.result_types import MultipleActionsResult
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
    """
    from engine.game_state import game_state
    
    player = game_state.player
    # Access enemies through current_combat, not combat_state
    combat = game_state.current_combat
    enemies = combat.enemies if combat else []

    if target_type == TargetType.SELF:
        return [player]
    elif target_type == TargetType.ENEMY_LOWEST_HP:
        alive_enemies = [e for e in enemies if e.hp > 0]
        return [min(alive_enemies, key=lambda e: e.hp) if alive_enemies else None]
    elif target_type == TargetType.ENEMY_RANDOM:
        import random
        alive_enemies = [e for e in enemies if e.hp > 0]
        return [random.choice(alive_enemies) if alive_enemies else None]
    elif target_type == TargetType.ENEMY_ALL:
        return [e for e in enemies if e.hp > 0]
    elif target_type == TargetType.ENEMY_SELECT:
        alive_enemies = [e for e in enemies if e.hp > 0]
        return alive_enemies
    else:
        raise ValueError(f"Unsupported TargetType: {target_type}")
    
    
