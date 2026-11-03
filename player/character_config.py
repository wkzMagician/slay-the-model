"""
Character configuration system for extensible character definitions.

Provides CharacterConfig class and @register_character decorator
to define character-specific stats, starting deck, and relics.
"""
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass


@dataclass
class CharacterConfig:
    """Configuration data for a character.

    Attributes:
        name: Character name (e.g., "Ironclad", "Silent")
        display_name: Display name for UI (e.g., "Ironclad", "Silent")
        max_hp: Starting max HP
        energy: Energy per turn
        gold: Starting gold
        orb_slots: Number of orb slots (default 0)
        potion_limit: Potion slot limit (default 3)
        deck: List of card IDs for starting deck
        starting_relics: List of relic IDs for starting relics
        draw_count: Base draw count per turn (default 5)
        playable: Whether the character should be exposed as a playable choice
        unplayable_reason: Explicit reason when a registered character is not yet playable
    """
    name: str
    display_name: str
    max_hp: int
    energy: int
    gold: int
    deck: List[str]
    starting_relics: List[str]
    orb_slots: int = 0
    potion_limit: int = 3
    draw_count: int = 5
    playable: bool = True
    unplayable_reason: Optional[str] = None


# Global registry for character configurations
_character_registry: Dict[str, CharacterConfig] = {}


def register_character(
    name: str,
    display_name: str,
    max_hp: int,
    energy: int,
    gold: int,
    deck: List[str],
    starting_relics: List[str],
    orb_slots: int = 0,
    potion_limit: int = 3,
    draw_count: int = 5,
    playable: bool = True,
    unplayable_reason: Optional[str] = None,
) -> Callable:
    """Decorator to register a character configuration.

    Usage:
        @register_character(
            name="ironclad",
            display_name="Ironclad",
            max_hp=80,
            energy=3,
            gold=99,
            deck=["ironclad.Strike", "ironclad.Defend", ...],
            starting_relics=["BurningBlood"],
        )
        class IroncladConfig:
            pass

    Args:
        name: Internal name for character
        display_name: Display name for UI
        max_hp: Starting max HP
        energy: Energy per turn
        gold: Starting gold
        deck: List of card IDs (must be registered in card registry)
        starting_relics: List of relic IDs (must be registered in relic registry)
        orb_slots: Number of orb slots
        potion_limit: Potion slot limit
        draw_count: Base draw count per turn
        playable: Whether the character should be listed as playable
        unplayable_reason: Explicit reason when a character is registered but not playable

    Returns:
        Decorator function
    """
    def decorator(cls):
        config = CharacterConfig(
            name=name,
            display_name=display_name,
            max_hp=max_hp,
            energy=energy,
            gold=gold,
            deck=deck,
            starting_relics=starting_relics,
            orb_slots=orb_slots,
            potion_limit=potion_limit,
            draw_count=draw_count,
            playable=playable,
            unplayable_reason=unplayable_reason,
        )
        _character_registry[name] = config
        cls.config = config
        return cls

    return decorator


def get_character_config(name: str) -> Optional[CharacterConfig]:
    """Get character configuration by name.

    Args:
        name: Character name (e.g., "ironclad", "Ironclad")

    Returns:
        CharacterConfig if found, None otherwise
    """
    if name in _character_registry:
        return _character_registry[name]

    name_lower = name.lower()
    for key, config in _character_registry.items():
        if key.lower() == name_lower:
            return config

    return None


def list_characters(playable_only: bool = False) -> List[str]:
    """List registered character names.

    Args:
        playable_only: When True, return only playable character names.

    Returns:
        List of character names
    """
    if not playable_only:
        return list(_character_registry.keys())
    return [name for name, config in _character_registry.items() if config.playable]
# Register Ironclad character
@register_character(
    name="ironclad",
    display_name="Ironclad",
    max_hp=80,
    energy=3,
    gold=99,
    deck=[
        "ironclad.Strike", "ironclad.Strike", "ironclad.Strike", "ironclad.Strike", "ironclad.Strike",
        "ironclad.Defend", "ironclad.Defend", "ironclad.Defend", "ironclad.Defend",
        "ironclad.Bash",
    ],
    starting_relics=["BurningBlood"],
)
class IroncladConfig:
    """Ironclad character configuration"""
    pass
