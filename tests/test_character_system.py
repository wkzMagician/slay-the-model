#!/usr/bin/env python3
"""Tests for character system extensibility."""

import pytest

from player.player_factory import create_player, list_characters


def test_list_characters_returns_only_playable_characters():
    """Public character list should expose playable characters."""
    characters = list_characters()
    assert characters == ["Ironclad", "Silent"]


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


def test_case_insensitive():
    """Test case-insensitive character name handling."""
    variations = ["Ironclad", "ironclad", "IRONCLAD", "Silent", "silent", "SILENT"]

    expected = {
        "ironclad": "Ironclad",
        "silent": "Silent",
    }

    for name in variations:
        player = create_player(name)
        assert player.character == expected[name.lower()]


def test_unknown_character():
    """Test error handling for unknown character."""
    with pytest.raises(ValueError):
        create_player("NonExistentCharacter")
