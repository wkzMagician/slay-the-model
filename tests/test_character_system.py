#!/usr/bin/env python3
"""Tests for character system extensibility."""

import sys

import pytest

from player.player_factory import create_player, list_characters


def test_list_characters():
    """Test listing all available characters."""
    characters = list_characters()
    print(f"Available characters: {characters}")
    assert len(characters) > 0, "No characters registered"


def test_create_ironclad():
    """Test creating Ironclad player."""
    player = create_player("Ironclad")
    deck_names = [card.__class__.__name__ for card in player.card_manager.deck]
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

    print(f"Ironclad deck: {deck_names}")
    print(f"Ironclad relics: {relic_names}")

    failed = [msg for passed, msg in checks if not passed]
    assert not failed, "; ".join(failed)


def test_create_silent():
    """Test creating Silent player."""
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
        (len(player.card_manager.deck) == 10, f"Deck size: {len(player.card_manager.deck)} != 10"),
        (len(player.relics) == 1, f"Relics count: {len(player.relics)} != 1"),
    ]

    print(f"Silent deck: {deck_names}")
    print(f"Silent relics: {relic_names}")

    failed = [msg for passed, msg in checks if not passed]
    assert not failed, "; ".join(failed)


def test_case_insensitive():
    """Test case-insensitive character name handling."""
    variations = ["Ironclad", "ironclad", "IRONCLAD"]

    for name in variations:
        player = create_player(name)
        print(f"{name} -> {player.character}")
        assert player.character == "Ironclad"


def test_unknown_character():
    """Test error handling for unknown character."""
    with pytest.raises(ValueError):
        create_player("NonExistentCharacter")


if __name__ == "__main__":
    sys.exit(pytest.main([__file__]))
