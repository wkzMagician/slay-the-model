from typing import Optional
from entities.creature import Creature
from utils.types import TargetType 

def resolve_target(target_type: TargetType) -> Optional[Creature]:
    """Resolve target based on TargetType enum
    
    Args:
        target_type: TargetType enum value indicating the type of target to resolve
    
    Returns:
        Creature instance representing the resolved target
    """
    from engine.game_state import game_state
    player = game_state.player
    enemies = game_state.combat_state.enemies

    if target_type == TargetType.SELF:
        return player
    elif target_type == TargetType.ENEMY_LOWEST_HP:
        return min(enemies, key=lambda e: e.hp) if enemies else None
    elif target_type == TargetType.ENEMY_RANDOM:
        import random
        return random.choice(enemies) if enemies else None
    elif target_type == TargetType.ENEMY_ALL:
        return enemies
    elif target_type == TargetType.ENEMY_SELECT:
        # 这个应该提前让玩家选择目标。这里报错
        raise NotImplementedError("TargetType.ENEMY_SELECT requires player selection, which is not implemented in this function.")
    else:
        raise ValueError(f"Unsupported TargetType: {target_type}")
    