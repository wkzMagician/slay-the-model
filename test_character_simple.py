#!/usr/bin/env python3
"""Simple test script for character system."""

import sys
from player.player_factory import create_player, list_characters


def main():
    """Run simple character system tests."""
    print("\n")
    print("=" * 60)
    print("CHARACTER SYSTEM TEST")
    print("=" * 60)
    print()
    
    # Test 1: List characters
    print("Test 1: List available characters")
    characters = list_characters()
    print(f"Available characters: {characters}")
    print(f"Count: {len(characters)}")
    print()
    
    # Test 2: Create Ironclad
    print("Test 2: Create Ironclad player")
    try:
        player = create_player("Ironclad")
        print(f"Character: {player.character}")
        print(f"Max HP: {player.max_hp}")
        print(f"Energy: {player.energy}")
        print(f"Gold: {player.gold}")
        print(f"Namespace: {player.namespace}")
        print(f"Deck size: {len(player.card_manager.deck)}")
        print(f"Relics: {[r.__class__.__name__ for r in player.relics]}")
        print("PASS: Ironclad created successfully")
    except Exception as e:
        print(f"FAIL: {e}")
        return 1
    print()
    
    # Test 3: Create Silent
    print("Test 3: Create Silent player")
    try:
        player = create_player("Silent")
        print(f"Character: {player.character}")
        print(f"Max HP: {player.max_hp}")
        print(f"Energy: {player.energy}")
        print(f"Gold: {player.gold}")
        print(f"Namespace: {player.namespace}")
        print(f"Deck size: {len(player.card_manager.deck)}")
        print(f"Relics: {[r.__class__.__name__ for r in player.relics]}")
        print("PASS: Silent created successfully")
    except Exception as e:
        print(f"FAIL: {e}")
        return 1
    print()
    
    # Test 4: Unknown character
    print("Test 4: Unknown character error handling")
    try:
        player = create_player("NonExistent")
        print(f"FAIL: Should have raised ValueError")
        return 1
    except ValueError as e:
        print(f"PASS: Correctly raised ValueError: {e}")
    print()
    
    print("=" * 60)
    print("All tests completed successfully!")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())