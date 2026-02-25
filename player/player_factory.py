# Import all character packages to ensure they are registered at module load time
import player.characters  # noqa: F401


def _import_character_cards(character: str):
    """Import cards for specified character to register them in registry.
    
    Args:
        character: Character name (e.g., "ironclad", "silent")
    """
    character = character.lower()
    if character in ("ironclad", "ironclad"):
        import cards.ironclad  # noqa: F401
    elif character in ("silent", "the_silent"):
        # Add when Silent is implemented
        pass
    # Add other characters here as they are implemented


def create_player(character=None):
    """Create a player with character-specific starting deck and stats.
    
    Args:
        character: Character name (e.g., "Ironclad", "ironclad", "Silent")
                 If None, uses default character from config
    
    Returns:
        Initialized Player instance with character-specific configuration
    
    Raises:
        ValueError: If character name is not found in registry
    """
    from player.player import Player
    from player.character_config import get_character_config
    from player.card_manager import CardManager
    from cards.namespaces import get_namespace_for_character
    from utils.registry import get_registered_instance
    
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
    
    # Import cards for this character BEFORE creating player
    # This ensures cards are registered in the registry
    _import_character_cards(character)
    
    # Create player with character stats
    player = Player(
        max_hp=char_config.max_hp,
        max_energy=char_config.energy
    )
    player.character = char_config.display_name
    player.namespace = get_namespace_for_character(char_config.display_name)
    player._gold = char_config.gold
    player.base_draw_count = char_config.draw_count
    
    # Create starting deck from card IDs
    starting_deck = []
    for card_id in char_config.deck:
        # Card IDs in character_config are "namespace.ClassName" format
        # Registry stores cards by class name only (capitalized)
        # Extract class name from "namespace.ClassName" and capitalize it
        if "." in card_id:
            class_name = card_id.split(".")[-1].capitalize()
        else:
            class_name = card_id.capitalize()
        
        # Get card instance from registry
        card = get_registered_instance("card", class_name)
        if card is None:
            raise ValueError(f"Card not found in registry: {card_id} (tried {class_name})")
        starting_deck.append(card)
    
    # Initialize card manager with starting deck
    player.card_manager = CardManager(starting_deck)
    
    # Add starting relics
    from relics.relics import create_relic_instance
    from utils.registry import get_registered
    for relic_id in char_config.starting_relics:
        # Get relic class from registry
        relic_class = get_registered("relic", relic_id)
        if relic_class is None:
            raise ValueError(f"Relic not found in registry: {relic_id}")
        relic = create_relic_instance(relic_class)
        player.relics.append(relic)
    
    return player


def list_characters():
    """List all available characters.
    
    Returns:
        List of character names (display names)
    """
    from player.character_config import get_character_config
    
    # Get all registered character configs
    from player.character_config import list_characters as list_char_names
    char_names = list_char_names()
    
    # Return display names
    display_names = []
    for name in char_names:
        config = get_character_config(name)
        if config:
            display_names.append(config.display_name)
    
    return display_names
