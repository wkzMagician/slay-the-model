"""
Dynamic value resolution system for cards and enemies.
Handles combat value calculations with powers, stances, and other modifiers.
"""

from typing import Optional, Any, TYPE_CHECKING
from entities.creature import Creature
from utils.types import StatusType

# Type hints only (avoid circular imports)
if TYPE_CHECKING:
    from cards.base import Card
    from player.player import Player


# ============ Card Value Resolution ============

def resolve_card_value(card, value_type: str) -> int:
    """
    Resolve dynamic card value
    
    Args:
        card: Card instance
        value_type: Value type ('damage', 'block')
    
    Returns:
        Dynamically calculated value
    """
    # Handle boolean flags
    if value_type in ['exhaust', 'ethereal', 'retain', 'innate']:
        return bool(getattr(card, f"_{value_type}", False))
    
    # Get base value from property
    base_value = getattr(card, value_type, 0)
    
    # If value is callable (for lambda deferred calculation)
    if callable(base_value):
        base_value = base_value()
    
    # Resolve different value types
    if value_type == 'damage':
        return resolve_card_damage(card)
    elif value_type == 'block':
        return resolve_card_block(card)
    else:
        # Handle type conversion safely - check if value is numeric or already int
        if isinstance(base_value, (int, float)):
            return int(base_value)
        elif isinstance(base_value, bool):
            # Handle boolean explicitly (avoid converting True to 1)
            return 1 if base_value else 0
        else:
            # Try to convert, fall back to 0 if conversion fails
            try:
                return int(base_value)  # type: ignore
            except (TypeError, ValueError):
                return 0


def resolve_card_damage(card: 'Card') -> int:
    """
    Resolve damage value (only considers attacker's abilities, not defender)
    
    Calculation order:
    1. Base damage (card.damage)
    2. + StrengthPower
    3. * 0.5 if has WeakPower
    4. * Multiplier (Rage/Divine stances)
    
    Args:
        card: Card instance
        source: Source creature (usually player)
    
    Returns:
        Resolved damage value
    """
    from engine.game_state import game_state
    player = game_state.player
    
    damage = card.damage
    
    # 1. Strength bonus
    strength_power = player.get_power('strength')
    if strength_power:
        damage += strength_power.amount
    
    # 2. Heavy Blade special handling (strength multiplied)
    if hasattr(card, 'get_magic_value'):
        strength_mult = card.get_magic_value('strength_mult', 0)
        if strength_mult and strength_power:
            damage += (strength_mult - 1) * strength_power.amount
    
    # 3. Weak effect (25% damage reduction)
    weak_power = player.get_power('weak')
    if weak_power:
        damage = int(damage * 0.75)
    
    # 4. Stance multiplier (Rage/Divine)
    status = player.status_manager.status
    if status == StatusType.WRATH:
        damage *= 2
    elif status == StatusType.DIVINITY:
        damage = int(damage * 3)
    
    # 5. Akabeko relic bonus: first attack deals 8 additional damage (only in combat)
    if hasattr(card, 'card_type') and card.card_type == "Attack":
        # Only apply combat-specific bonuses when in combat
        if game_state.current_combat is not None:
            first_attack_played = game_state.current_combat.combat_state.turn_attack_cards_played == 0
            
            # Check if player has Akabeko relic
            has_akabeko = any(r.__class__.__name__ == 'Akabeko' for r in player.relics)
            
            if has_akabeko and first_attack_played:
                damage += 8
                # Mark that first attack has been played
                game_state.current_combat.combat_state.turn_attack_cards_played += 1
    
    return max(0, damage)


def resolve_potential_damage(base_damage: int, attacker: Creature, 
                         target: Creature) -> int:
    """
    Resolve final damage value
    
    Calculation order:
    1. Resolve callable damage if needed
    2. attacker's Strength
    3. attacker's stance multiplier (Rage/Divine)
    4. attacker's Weak
    5. target's Vulnerable
    6. target's other power (e.g. Slow)
    7. target's stance multiplier (Rage)
    """
    # 0. Resolve callable damage first
    damage = base_damage() if callable(base_damage) else base_damage
    
    # Debug: Check if damage is a list
    if isinstance(damage, list):
        print(f"[ERROR] resolve_potential_damage received list: {damage}, base_damage={base_damage}")
        damage = damage[0] if damage else 0  # Take first element or 0
    # 1. Attacker's Strength
    strength_power = attacker.get_power('strength')
    if strength_power:
        damage += strength_power.amount
    # 2. Attacker's stance multiplier
    from player.player import Player
    if isinstance(attacker, Player):
        attacker_status = attacker.status_manager.status
        if attacker_status == StatusType.WRATH:
            damage *= 2
        elif attacker_status == StatusType.DIVINITY:
            damage = int(damage * 3)
    # 3. Attacker's Weak (25% damage reduction)
    weak_power = attacker.get_power('weak')
    if weak_power:
        damage = int(damage * 0.75)
    # 4. Target's Vulnerable
    if target is not None:
        vulnerable_power = target.get_power('vulnerable')
        if vulnerable_power:
            damage = int(damage * 1.5)
        # 5. Target's other powers (e.g. Slow)
        # feature: SLowPower
        # 6. Target's stance multiplier
        from player.player import Player
        if isinstance(target, Player):
            target_status = target.status_manager.status
            if target_status == StatusType.WRATH:
                damage *= 2
            
    return max(0, damage)


def resolve_card_block(card: 'Card') -> int:
    """Resolve block value"""
    block = card.block
    from engine.game_state import game_state
    player = game_state.player
    # player有Frail会减少25%格挡
    frail_power = player.get_power('frail')
    if frail_power:
        block = int(block * 0.75)
    return int(block)


# 充能球的魔法值获取
def resolve_orb_value(value: int) -> int:
    """Resolve orb value considering Focus power"""
    from engine.game_state import game_state
    player = game_state.player
    focus_power = player.get_power('focus')
    if focus_power:
        value += focus_power.amount
    return max(0, value)

def resolve_orb_damage(base_damage: int, target: Creature) -> int:
    from engine.game_state import game_state
    player = game_state.player
    damage = resolve_orb_value(base_damage)
    if target.get_power('Lock-On') != None:
        damage *= 1.5
    return int(damage)


def get_magic_value(card, magic_key: str, default: Any = 0) -> Any:
    """Get value from magic dictionary"""
    if not hasattr(card, '_magic'):
        return default
    return card._magic.get(magic_key, default)