"""
Dynamic value resolution system for cards and enemies.
Handles combat value calculations with powers, stances, and other modifiers.
"""

import math
from typing import Optional, Any, TYPE_CHECKING, cast
from entities.creature import Creature
from utils.types import CardType, DamageType, StatusType
from utils.damage_phase import DamagePhase

# Type hints only (avoid circular imports)
if TYPE_CHECKING:
    from cards.base import Card
    from player.player import Player


# ============ Card Value Resolution ============

def resolve_card_value(card, value_type: str, target: Optional[Creature] = None) -> int:
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
        return resolve_card_damage(card, target=target)
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


def attack_base_damage(card: 'Card') -> int:
    """Base damage sent into the damage pipeline, before Strength is added once."""
    from engine.game_state import game_state

    base_damage = card.damage
    if callable(base_damage):
        base_damage = base_damage()

    player = game_state.player
    if player is None or not hasattr(card, "get_magic_value"):
        return base_damage

    strength_power = player.get_power("Strength")
    if strength_power is None:
        return base_damage

    strength_mult = card.get_magic_value("strength_mult", 0)
    if strength_mult:
        base_damage += (strength_mult - 1) * strength_power.amount
    return base_damage


def resolve_card_damage(card: 'Card', target: Optional[Creature] = None) -> int:
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
    base_damage = attack_base_damage(card)
    damage_type = DamageType.PHYSICAL if getattr(card, "card_type", None) == CardType.ATTACK else DamageType.MAGICAL
    return resolve_potential_damage(base_damage, player, target=target, card=card, damage_type=damage_type)


def _is_physical_attack(damage_type) -> bool:
    return damage_type in {DamageType.PHYSICAL, "attack"}


def _damage_priority(modifier) -> int:
    return getattr(modifier, "damage_priority", 5)


def _modifiers_in_phase(modifiers, phase: DamagePhase):
    matched = [
        modifier
        for modifier in modifiers
        if getattr(modifier, "modify_phase", DamagePhase.ADDITIVE) == phase
        and not getattr(modifier, "is_back_attack", False)
    ]
    return sorted(matched, key=_damage_priority)


def _apply_damage_dealt(damage, modifier, card, target):
    try:
        return cast(Any, modifier).modify_damage_dealt(damage, card=card, target=target)
    except TypeError:
        return cast(Any, modifier).modify_damage_dealt(damage)


def _apply_dealt_phase(damage, attacker, phase: DamagePhase, card, target):
    from player.player import Player

    if attacker is not None and hasattr(attacker, "powers"):
        for power in _modifiers_in_phase(attacker.powers, phase):
            if hasattr(power, "modify_damage_dealt"):
                damage = _apply_damage_dealt(damage, power, card, target)
    if isinstance(attacker, Player) and hasattr(attacker, "relics"):
        for relic in _modifiers_in_phase(attacker.relics, phase):
            if hasattr(relic, "modify_damage_dealt"):
                damage = cast(Any, relic).modify_damage_dealt(damage, card=card, target=target)
    return damage


def _apply_taken_phase(damage, target, attacker, phase: DamagePhase, damage_type, *, for_card_snapshot=False):
    from player.player import Player

    if target is None:
        return damage
    if hasattr(target, "powers"):
        for power in _modifiers_in_phase(target.powers, phase):
            if for_card_snapshot and getattr(power, "damage_is_runtime", False):
                continue
            if hasattr(power, "modify_damage_taken"):
                damage = cast(Any, power).modify_damage_taken(damage)
    # Capping relics (Torii) run when damage is received, not on the card.
    if for_card_snapshot and phase == DamagePhase.CAPPING:
        return damage
    if isinstance(target, Player) and hasattr(target, "relics"):
        for relic in _modifiers_in_phase(target.relics, phase):
            if hasattr(relic, "modify_damage_taken"):
                damage = cast(Any, relic).modify_damage_taken(
                    damage,
                    source=attacker,
                    damage_type=damage_type,
                )
    return damage


def _apply_back_attack(damage, attacker):
    if attacker is None:
        return damage
    for power in getattr(attacker, "powers", []):
        if getattr(power, "is_back_attack", False):
            return int(power.modify_damage_dealt(damage))
    return damage


def resolve_potential_damage(base_damage: int, attacker: Optional[Creature], 
                         target: Optional[Creature], card=None, damage_type: str | None = None,
                         *, for_card_snapshot: bool = False) -> int:
    """
    Resolve final damage value with one floor at the end.

    Physical attacks: additive, attacker multipliers, stance, incoming
    multipliers, back attack, final modifiers, then capping.
    Other damage types only receive capping modifiers.
    """
    from player.player import Player

    is_physical = _is_physical_attack(damage_type)

    damage = base_damage() if callable(base_damage) else base_damage
    if isinstance(damage, list):
        print(f"[ERROR] resolve_potential_damage received list: {damage}, base_damage={base_damage}")
        damage = damage[0] if damage else 0
    damage = float(damage)

    if is_physical:
        damage = _apply_dealt_phase(damage, attacker, DamagePhase.ADDITIVE, card, target)
        damage = _apply_dealt_phase(damage, attacker, DamagePhase.MULTIPLICATIVE, card, target)

        if isinstance(attacker, Player):
            attacker_status = attacker.status_manager.status
            if attacker_status == StatusType.WRATH:
                damage *= 2
            elif attacker_status == StatusType.DIVINITY:
                damage *= 3

        if target is not None:
            if hasattr(target, "get_damage_taken_multiplier"):
                damage *= target.get_damage_taken_multiplier()
            if isinstance(target, Player) and target.status_manager.status == StatusType.WRATH:
                damage *= 2
            damage = _apply_taken_phase(
                damage, target, attacker, DamagePhase.MULTIPLICATIVE, damage_type
            )

        damage = _apply_back_attack(damage, attacker)
        damage = _apply_taken_phase(damage, target, attacker, DamagePhase.FINAL, damage_type)

    damage = _apply_taken_phase(
        damage, target, attacker, DamagePhase.CAPPING, damage_type,
        for_card_snapshot=for_card_snapshot,
    )
    return max(0, math.floor(damage))


def resolve_calculated_damage(damage: int, attacker, target, damage_type) -> int:
    """Apply only live defenses to an already calculated card attack.

    Flight and enemy Intangible belong to calculateCardDamage. Invincible
    belongs to damage(), as does the player's extra Intangible safeguard.
    Block and Buffer are handled by DealDamageAction after this step.
    """
    from player.player import Player
    from powers.definitions.intangible import IntangiblePower

    for power in _modifiers_in_phase(getattr(target, "powers", []), DamagePhase.CAPPING):
        if getattr(power, "damage_is_runtime", False) or (
            isinstance(target, Player) and isinstance(power, IntangiblePower)
        ):
            damage = cast(Any, power).modify_damage_taken(damage)
    if isinstance(target, Player):
        for relic in _modifiers_in_phase(target.relics, DamagePhase.CAPPING):
            if hasattr(relic, "modify_damage_taken"):
                damage = cast(Any, relic).modify_damage_taken(
                    damage, source=attacker, damage_type=damage_type,
                )
    return max(0, math.floor(damage))


def _apply_block_phase(block, owner, phase: DamagePhase):
    from player.player import Player

    if hasattr(owner, "powers"):
        for power in _modifiers_in_phase(owner.powers, phase):
            if hasattr(power, "modify_block_gained"):
                block = cast(Any, power).modify_block_gained(block)
    if isinstance(owner, Player) and hasattr(owner, "relics"):
        for relic in _modifiers_in_phase(owner.relics, phase):
            if hasattr(relic, "modify_block_gained"):
                block = cast(Any, relic).modify_block_gained(block)
    return block


def resolve_block_gained(base_block, owner=None) -> int:
    """Apply card-block modifiers, then floor once.

    Dexterity and Frail belong here. GainBlockAction adds the returned number
    as-is, so powers, orbs, and relics stay outside this function.
    """
    block = base_block() if callable(base_block) else base_block
    block = float(block)
    if owner is not None:
        block = _apply_block_phase(block, owner, DamagePhase.ADDITIVE)
        block = _apply_block_phase(block, owner, DamagePhase.MULTIPLICATIVE)
    return max(0, math.floor(block))


def resolve_card_block(card: 'Card') -> int:
    """Resolve the block a card grants when played or previewed."""
    from engine.game_state import game_state

    return resolve_block_gained(card.block, game_state.player)


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
