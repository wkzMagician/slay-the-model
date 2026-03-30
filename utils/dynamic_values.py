"""
Dynamic value resolution system for cards and enemies.
Handles combat value calculations with powers, stances, and other modifiers.
"""

from typing import Optional, Any, TYPE_CHECKING
from entities.creature import Creature
from utils.types import StatusType
from utils.damage_phase import DamagePhase

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
    Resolve damage value for card preview (only considers attacker's abilities).
    
    This is a thin wrapper around resolve_potential_damage for preview purposes.
    It applies all damage modifiers except target-specific ones (Vulnerable, Intangible).
    
    Args:
        card: Card instance
    
    Returns:
        Resolved damage value for preview
    """
    from engine.game_state import game_state
    player = game_state.player
    
    # Get base damage
    base_damage = card.damage
    if callable(base_damage):
        base_damage = base_damage()
    
    # Handle Heavy Blade special case - extra strength scaling
    strength_power = player.get_power('strength')
    if strength_power and hasattr(card, 'get_magic_value'):
        strength_mult = card.get_magic_value('strength_mult', 0)
        if strength_mult and strength_mult:
            # Heavy Blade: extra strength bonus added to base
            base_damage += (strength_mult - 1) * strength_power.amount
    
    # Use unified pipeline with no target (preview mode)
    return resolve_potential_damage(base_damage, player, target=None, card=card)


def resolve_potential_damage(base_damage: int, attacker: Creature, 
                         target: Creature, card=None) -> int:
    """
    Resolve final damage value with unified phased pipeline.
    
    This is the SINGLE SOURCE OF TRUTH for damage calculation.
    All damage modifiers should be applied here, not in DealDamageAction.
    
    Phase order (CRITICAL - additive before multiplicative before capping):
    1. Normalize damage (callable/list -> int)
    2. ADDITIVE phase: Powers first, then Relics
    3. MULTIPLICATIVE phase: Powers first, then Relics
    4. CAPPING phase: Powers first, then Relics
    5. Clamp to non-negative
    
    For each phase, the order is ALWAYS: Powers -> Relics
    
    Args:
        base_damage: Base damage value (int or callable returning int)
        attacker: Creature dealing damage
        target: Creature receiving damage (can be None for preview)
        card: Card being played (optional, for PenNib etc.)
    
    Returns:
        Final resolved damage value
    """
    from player.player import Player
    
    # ====================
    # Phase 1: Normalize
    # ====================
    damage = base_damage() if callable(base_damage) else base_damage
    
    # Defensive: handle case where damage is accidentally a list
    if isinstance(damage, list):
        print(f"[ERROR] resolve_potential_damage received list: {damage}, base_damage={base_damage}")
        damage = damage[0] if damage else 0
    
    # ====================
    # Phase 2: ADDITIVE (加算)
    # e.g., Strength +3, Dexterity for block
    # ====================
    
    # 2a. Attacker's powers (ADDITIVE phase)
    if attacker and hasattr(attacker, 'powers'):
        for power in attacker.powers:
            if getattr(power, 'modify_phase', DamagePhase.ADDITIVE) == DamagePhase.ADDITIVE:
                if hasattr(power, 'modify_damage_dealt'):
                    try:
                        damage = power.modify_damage_dealt(damage, card=card, target=target)
                    except TypeError:
                        damage = power.modify_damage_dealt(damage)
    
    # 2b. Attacker's relics (ADDITIVE phase, Player only)
    if isinstance(attacker, Player) and hasattr(attacker, 'relics'):
        for relic in attacker.relics:
            if getattr(relic, 'modify_phase', DamagePhase.ADDITIVE) == DamagePhase.ADDITIVE:
                if hasattr(relic, 'modify_damage_dealt'):
                    damage = relic.modify_damage_dealt(damage, card=card, target=target)
    
    # ====================
    # Phase 3: MULTIPLICATIVE (乘算)
    # e.g., Weak 0.75x, Vulnerable 1.5x, PenNib 2x
    # ====================
    
    # 3a. Attacker's powers (MULTIPLICATIVE phase)
    if attacker and hasattr(attacker, 'powers'):
        for power in attacker.powers:
            if getattr(power, 'modify_phase', DamagePhase.ADDITIVE) == DamagePhase.MULTIPLICATIVE:
                if hasattr(power, 'modify_damage_dealt'):
                    try:
                        damage = power.modify_damage_dealt(damage, card=card, target=target)
                    except TypeError:
                        damage = power.modify_damage_dealt(damage)
    
    # 3b. Attacker's relics (MULTIPLICATIVE phase, Player only)
    if isinstance(attacker, Player) and hasattr(attacker, 'relics'):
        for relic in attacker.relics:
            if getattr(relic, 'modify_phase', DamagePhase.ADDITIVE) == DamagePhase.MULTIPLICATIVE:
                if hasattr(relic, 'modify_damage_dealt'):
                    damage = relic.modify_damage_dealt(damage, card=card, target=target)
    
    # 3c. Attacker's stance multiplier (Player only)
    if isinstance(attacker, Player):
        attacker_status = attacker.status_manager.status
        if attacker_status == StatusType.WRATH:
            damage *= 2
        elif attacker_status == StatusType.DIVINITY:
            damage = int(damage * 3)
    
    # 3d. Target's incoming multiplicative modifiers
    if target is not None:
        # Target's Vulnerable (50% more damage)
        if hasattr(target, 'get_damage_taken_multiplier'):
            multiplier = target.get_damage_taken_multiplier()
            damage = int(damage * multiplier)
        
        # Target's stance multiplier (Player only)
        if isinstance(target, Player):
            target_status = target.status_manager.status
            if target_status == StatusType.WRATH:
                damage *= 2
        
        # Target's powers (MULTIPLICATIVE phase for damage taken)
        if hasattr(target, 'powers'):
            for power in target.powers:
                if getattr(power, 'modify_phase', DamagePhase.ADDITIVE) == DamagePhase.MULTIPLICATIVE:
                    if hasattr(power, 'modify_damage_taken'):
                        damage = power.modify_damage_taken(damage)
        
        # Target's relics (MULTIPLICATIVE phase, Player only)
        if isinstance(target, Player) and hasattr(target, 'relics'):
            for relic in target.relics:
                if getattr(relic, 'modify_phase', DamagePhase.ADDITIVE) == DamagePhase.MULTIPLICATIVE:
                    if hasattr(relic, 'modify_damage_taken'):
                        damage = relic.modify_damage_taken(damage, source=attacker)
    
    # ====================
    # Phase 4: CAPPING (限定)
    # e.g., Intangible caps all damage to 1
    # ====================
    
    # 4a. Target's powers (CAPPING phase for damage taken)
    if target is not None and hasattr(target, 'powers'):
        for power in target.powers:
            if getattr(power, 'modify_phase', DamagePhase.ADDITIVE) == DamagePhase.CAPPING:
                if hasattr(power, 'modify_damage_taken'):
                    damage = power.modify_damage_taken(damage)
    
    # 4b. Target's relics (CAPPING phase, Player only)
    if isinstance(target, Player) and hasattr(target, 'relics'):
        for relic in target.relics:
            if getattr(relic, 'modify_phase', DamagePhase.ADDITIVE) == DamagePhase.CAPPING:
                if hasattr(relic, 'modify_damage_taken'):
                    damage = relic.modify_damage_taken(damage, source=attacker)
    
    # ====================
    # Phase 5: Clamp
    # ====================
    return max(0, int(damage))


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