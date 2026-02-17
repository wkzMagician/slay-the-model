from typing import Optional, Union, List
from entities.creature import Creature
from utils.types import TargetType 

def resolve_target(target_type: TargetType, show_selection: bool = True) -> Optional[Union[Creature, List[Creature]]]:
    """Resolve target based on TargetType enum
    
    Args:
        target_type: TargetType enum value indicating the type of target to resolve
        show_selection: Whether to show selection UI for human mode (default: True)
    
    Returns:
        Creature instance or list of Creatures representing the resolved target
    """
    from engine.game_state import game_state
    player = game_state.player
    # Access enemies through current_combat, not combat_state
    combat = game_state.current_combat
    enemies = combat.enemies if combat else []

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
        alive_enemies = [e for e in enemies if not e.is_dead()]
        
        # If only one enemy or not showing selection, auto-select
        if len(alive_enemies) <= 1 or not show_selection:
            return alive_enemies[0] if alive_enemies else None
        
        # For human mode with multiple enemies, show selection UI
        mode = game_state.config.get("mode", "debug")
        if mode == "human":
            from utils.option import Option
            from localization import LocalStr, t
            
            # Show target selection header
            print(f"\n{t('combat.select_target', default='=== Select Target ===')}")
            
            # Show available enemies
            for i, enemy in enumerate(alive_enemies):
                print(f"{i+1}. {enemy.name} (HP: {enemy.hp}/{enemy.max_hp})")
            
            # Get player input
            while True:
                try:
                    prompt_text = t("ui.target_prompt", default=f"Choose target (1-{len(alive_enemies)}): ")
                    input_str = input(prompt_text).strip()
                    selected_idx = int(input_str) - 1
                    if 0 <= selected_idx < len(alive_enemies):
                        # Print selected target
                        print(f"\n{t('ui.selected', default='Selected:')}")
                        print(f"  1. {alive_enemies[selected_idx].name}")
                        return alive_enemies[selected_idx]
                    else:
                        print(t("ui.invalid_option", default=f"Invalid option: {selected_idx + 1}"))
                except (ValueError, EOFError):
                    print(t("ui.invalid_input", default="Invalid input format. Enter a number."))
        else:
            # Auto mode: select first alive enemy
            return alive_enemies[0] if alive_enemies else None
    else:
        raise ValueError(f"Unsupported TargetType: {target_type}")
    