#!/usr/bin/env python3
"""Tests for character system extensibility."""

import pytest

from player.character_config import get_character_config
from player.player_factory import create_player, list_characters


def test_list_characters_returns_only_playable_characters():
    """Public character list should expose playable characters."""
    characters = list_characters()
    assert characters == ["Ironclad", "Silent", "Defect", "Watcher"]


def test_create_defect_character_config():
    """Defect should be registered with the expected starter config."""
    config = get_character_config("Defect")

    assert config is not None
    assert config.display_name == "Defect"
    assert config.max_hp == 75
    assert config.energy == 3
    assert config.gold == 99
    assert config.deck == [
        "defect.strike",
        "defect.strike",
        "defect.strike",
        "defect.strike",
        "defect.defend",
        "defect.defend",
        "defect.defend",
        "defect.defend",
        "defect.zap",
        "defect.dualcast",
    ]
    assert config.starting_relics == ["CrackedCore"]
    assert config.orb_slots == 3
    assert config.potion_limit == 3
    assert config.draw_count == 5


def test_create_defect():
    """Defect should be a playable character with the expected starter kit."""
    player = create_player("Defect")
    deck_names = [card.__class__.__name__ for card in player.card_manager.deck]
    relic_names = [r.__class__.__name__ for r in player.relics]

    checks = [
        (player.character == "Defect", f"Character name: {player.character} != Defect"),
        (player.max_hp == 75, f"Max HP: {player.max_hp} != 75"),
        (player.energy == 3, f"Energy: {player.energy} != 3"),
        (player.gold == 99, f"Gold: {player.gold} != 99"),
        (player.namespace == "defect", f"Namespace: {player.namespace} != defect"),
        (player.base_draw_count == 5, f"Draw count: {player.base_draw_count} != 5"),
        (player.orb_manager.max_orb_slots == 3, f"Orb slots: {player.orb_manager.max_orb_slots} != 3"),
        (player.potion_limit == 3, f"Potion limit: {player.potion_limit} != 3"),
        (len(player.card_manager.deck) == 10, f"Deck size: {len(player.card_manager.deck)} != 10"),
        (deck_names.count("Strike") == 4, f"Defect should start with 4 Strikes, got {deck_names}"),
        (deck_names.count("Defend") == 4, f"Defect should start with 4 Defends, got {deck_names}"),
        ("Zap" in deck_names, f"Zap missing from deck: {deck_names}"),
        ("Dualcast" in deck_names, f"Dualcast missing from deck: {deck_names}"),
        (len(player.relics) == 1, f"Relics count: {len(player.relics)} != 1"),
        ("CrackedCore" in relic_names, f"CrackedCore not in relics: {relic_names}"),
    ]

    failed = [msg for passed, msg in checks if not passed]
    assert not failed, "; ".join(failed)


def test_create_ironclad():
    """Test creating Ironclad player."""
    player = create_player("Ironclad")
    relic_names = [r.__class__.__name__ for r in player.relics]

    checks = [
        (player.character == "Ironclad", f"Character name: {player.character} != Ironclad"),
        (player.max_hp == 80, f"Max HP: {player.max_hp} != 80"),
        (player.energy == 3, f"Energy: {player.energy} != 3"),
        (player.gold == 99, f"Gold: {player.gold} != 99"),
        (player.namespace == "ironclad", f"Namespace: {player.namespace} != ironclad"),
        (player.base_draw_count == 5, f"Draw count: {player.base_draw_count} != 5"),
        (len(player.card_manager.deck) == 10, f"Deck size: {len(player.card_manager.deck)} != 10"),
        (len(player.relics) == 1, f"Relics count: {len(player.relics)} != 1"),
        ("BurningBlood" in relic_names, f"BurningBlood not in relics: {relic_names}"),
    ]

    failed = [msg for passed, msg in checks if not passed]
    assert not failed, "; ".join(failed)


def test_create_silent():
    """Silent should be a playable character with the expected starter kit."""
    player = create_player("Silent")
    deck_names = [card.__class__.__name__ for card in player.card_manager.deck]
    relic_names = [r.__class__.__name__ for r in player.relics]

    checks = [
        (player.character == "Silent", f"Character name: {player.character} != Silent"),
        (player.max_hp == 70, f"Max HP: {player.max_hp} != 70"),
        (player.energy == 3, f"Energy: {player.energy} != 3"),
        (player.gold == 99, f"Gold: {player.gold} != 99"),
        (player.namespace == "silent", f"Namespace: {player.namespace} != silent"),
        (player.base_draw_count == 5, f"Draw count: {player.base_draw_count} != 5"),
        (len(player.card_manager.deck) == 12, f"Deck size: {len(player.card_manager.deck)} != 12"),
        (deck_names.count("Strike") == 5, f"Silent should start with 5 Strikes, got {deck_names}"),
        (deck_names.count("Defend") == 5, f"Silent should start with 5 Defends, got {deck_names}"),
        ("Neutralize" in deck_names, f"Neutralize missing from deck: {deck_names}"),
        ("Survivor" in deck_names, f"Survivor missing from deck: {deck_names}"),
        (len(player.relics) == 1, f"Relics count: {len(player.relics)} != 1"),
        ("RingOfTheSnake" in relic_names, f"RingOfTheSnake not in relics: {relic_names}"),
    ]

    failed = [msg for passed, msg in checks if not passed]
    assert not failed, "; ".join(failed)


def test_create_watcher():
    """Watcher should be a playable character with the expected starter kit."""
    player = create_player("Watcher")
    deck_names = [card.__class__.__name__ for card in player.card_manager.deck]
    relic_names = [r.__class__.__name__ for r in player.relics]

    checks = [
        (player.character == "Watcher", f"Character name: {player.character} != Watcher"),
        (player.max_hp == 72, f"Max HP: {player.max_hp} != 72"),
        (player.energy == 3, f"Energy: {player.energy} != 3"),
        (player.gold == 99, f"Gold: {player.gold} != 99"),
        (player.namespace == "watcher", f"Namespace: {player.namespace} != watcher"),
        (player.base_draw_count == 5, f"Draw count: {player.base_draw_count} != 5"),
        (len(player.card_manager.deck) == 10, f"Deck size: {len(player.card_manager.deck)} != 10"),
        (deck_names.count("Strike") == 4, f"Watcher should start with 4 Strikes, got {deck_names}"),
        (deck_names.count("Defend") == 4, f"Watcher should start with 4 Defends, got {deck_names}"),
        ("Eruption" in deck_names, f"Eruption missing from deck: {deck_names}"),
        ("Vigilance" in deck_names, f"Vigilance missing from deck: {deck_names}"),
        (len(player.relics) == 1, f"Relics count: {len(player.relics)} != 1"),
        ("PureWater" in relic_names, f"PureWater not in relics: {relic_names}"),
    ]

    failed = [msg for passed, msg in checks if not passed]
    assert not failed, "; ".join(failed)


def test_case_insensitive():
    """Test case-insensitive character name handling."""
    variations = [
        "Ironclad", "ironclad", "IRONCLAD",
        "Silent", "silent", "SILENT",
        "Defect", "defect", "DEFECT",
        "Watcher", "watcher", "WATCHER",
    ]

    expected = {
        "ironclad": "Ironclad",
        "silent": "Silent",
        "defect": "Defect",
        "watcher": "Watcher",
    }

    for name in variations:
        player = create_player(name)
        assert player.character == expected[name.lower()]


def test_character_config_case_insensitive():
    """Test case-insensitive character config lookup."""
    variations = ["Defect", "defect", "DEFECT"]

    for name in variations:
        config = get_character_config(name)
        assert config is not None
        assert config.display_name == "Defect"
        assert config.orb_slots == 3


def test_unknown_character():
    """Test error handling for unknown character."""
    with pytest.raises(ValueError):
        create_player("NonExistentCharacter")
