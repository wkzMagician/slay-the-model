import importlib

# Import all character packages to ensure they are registered at module load time
import player.characters  # noqa: F401


DEFAULT_UNPLAYABLE_CHARACTER_ERROR = "Character '{name}' is not playable yet"


def _import_character_cards(character: str):
    """Import cards for specified character to register them in registry.

    Args:
        character: Character name (e.g., "ironclad", "silent")
    """
    importlib.import_module(f"cards.{character.lower()}")


def _import_character_relics(character: str):
    """Import character-specific relics for the selected character."""
    importlib.import_module(f"relics.character.{character.lower()}")


def create_player(character=None, *, ascension: int = 0):
    """Create a player with character-specific starting deck and stats.

    Args:
        character: Character name (e.g., "Ironclad", "ironclad", "Silent")
                 If None, uses default character from config
        ascension: New-run ascension level; callers without a run default to A0.

    Returns:
        Initialized Player instance with character-specific configuration

    Raises:
        ValueError: If character name is not found in registry
    """
    from player.player import Player
    from player.character_config import get_character_config
    from player.card_manager import CardManager
    from cards.namespaces import CARD_NAMESPACES, get_namespace_for_character

    # Normalize character name
    if not character:
        from config.game_config import GameConfig
        config = GameConfig.load("config/game_config.yaml")
        character = config.character

    # Get character configuration
    char_config = get_character_config(character)
    if char_config is None:
        raise ValueError(f"Unknown character: {character}. "
                       f"Available characters: {list_characters()}")
    if not char_config.playable:
        raise ValueError(
            char_config.unplayable_reason
            or DEFAULT_UNPLAYABLE_CHARACTER_ERROR.format(name=char_config.display_name)
        )

    # Import cards for this character BEFORE creating player
    _import_character_cards(character)
    _import_character_relics(character)

    max_hp = char_config.max_hp
    if ascension >= 14:
        max_hp -= 5 if char_config.name.lower() == "ironclad" else 4
    player = Player(
        max_hp=max_hp,
        max_energy=char_config.energy
    )
    player.character = char_config.display_name
    player.namespace = get_namespace_for_character(char_config.display_name)
    player._gold = char_config.gold
    player.base_draw_count = char_config.draw_count
    player.base_orb_slots = char_config.orb_slots
    player.orb_manager.max_orb_slots = char_config.orb_slots
    player.potion_limit = char_config.potion_limit - (1 if ascension >= 11 else 0)
    if ascension >= 6:
        # MathUtils.round(maxHealth * 0.9f), for positive starting health.
        player.hp = (max_hp * 9 + 5) // 10

    starting_deck = []
    for card_id in char_config.deck:
        namespace, _, class_name = card_id.rpartition(".")
        namespace = namespace.lower() or player.namespace
        card_class = CARD_NAMESPACES.get(namespace, {}).get(class_name.lower())
        if card_class is None:
            raise ValueError(f"Card not found in namespace registry: {card_id}")
        starting_deck.append(card_class())

    if ascension >= 10:
        from cards.colorless.ascenders_bane import AscendersBane
        starting_deck.append(AscendersBane())

    player.card_manager = CardManager(starting_deck)

    from relics.relics import create_relic_instance
    from utils.registry import get_registered
    for relic_id in char_config.starting_relics:
        relic_class = get_registered("relic", relic_id)
        if relic_class is None:
            raise ValueError(f"Relic not found in registry: {relic_id}")
        relic = create_relic_instance(relic_class)
        player.relics.append(relic)

    return player


def list_characters():
    """List all available characters.

    Returns:
        List of playable character names (display names)
    """
    from player.character_config import get_character_config
    from player.character_config import list_characters as list_char_names

    display_names = []
    for name in list_char_names(playable_only=True):
        config = get_character_config(name)
        if config:
            display_names.append(config.display_name)

    return display_names
