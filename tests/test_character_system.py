#!/usr/bin/env python3
"""Tests for character system extensibility."""

import pytest

from player.player_factory import create_player, list_characters


UNIMPLEMENTED_SILENT_ERROR = "Character 'Silent' is not playable yet: starter cards are unavailable"


def test_list_characters_returns_only_playable_characters():
    """Public character list should only expose playable characters."""
    characters = list_characters()
    assert characters == ["Ironclad"]
    assert "Silent" not in characters


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
        (len(player.card_manager.deck) > 0, "Starter deck is empty"),
        ({"Strike", "Defend"}.issubset(set(deck_names)), f"Missing starter cards: {deck_names}"),
        ("BurningBlood" in relic_names, f"BurningBlood not in relics: {relic_names}"),
    ]

    failed = [msg for passed, msg in checks if not passed]
    assert not failed, "; ".join(failed)


def test_create_silent_reports_character_as_not_playable_yet():
    """Silent remains registered but must fail explicitly until starter cards exist."""
    with pytest.raises(ValueError, match=UNIMPLEMENTED_SILENT_ERROR):
        create_player("Silent")


def test_case_insensitive():
    """Test case-insensitive character name handling."""
    variations = ["Ironclad", "ironclad", "IRONCLAD"]

    for name in variations:
        player = create_player(name)
        assert player.character == "Ironclad"


def test_unknown_character():
    """Test error handling for unknown character."""
    with pytest.raises(ValueError):
        create_player("NonExistentCharacter")
