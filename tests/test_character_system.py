#!/usr/bin/env python3
"""Test script for character system extensibility.

This script tests:
1. Character configuration registration
2. Player creation with different characters
3. Character-specific properties (HP, gold, deck, relics)
4. Error handling for unknown characters
"""

import sys
from player.player_factory import create_player, list_characters


def test_list_characters():
    """Test listing all available characters."""
    print("=" * 60)
    print("TEST 1: List Available Characters")
    print("=" * 60)
    
    characters = list_characters()
    print(f"Available characters: {characters}")
    print(f"Count: {len(characters)}")
    print()
    
    if len(characters) == 0:
        print("❌ FAIL: No characters registered!")
        return False
    
    print("✓ PASS: Characters registered successfully\n")
    return True


def test_create_ironclad():
    """Test creating Ironclad player."""
    print("=" * 60)
    print("TEST 2: Create Ironclad Player")
    print("=" * 60)
    
    player = create_player("Ironclad")
    
    # Check basic properties
    print(f"Character: {player.character}")
    print(f"Max HP: {player.max_hp} (expected: 80)")
    print(f"Energy: {player.energy} (expected: 3)")
    print(f"Gold: {player.gold} (expected: 99)")
    print(f"Namespace: {player.namespace} (expected: ironclad)")
    print(f"Draw Count: {player.base_draw_count} (expected: 5)")
    print()
    
    # Check deck
    print(f"Deck size: {len(player.card_manager.deck)} (expected: 10)")
    deck_names = [card.__class__.__name__ for card in player.card_manager.deck]
    print(f"Deck composition: {deck_names}")
    print()
    
    # Check relics
    print(f"Relics count: {len(player.relics)} (expected: 1)")
    relic_names = [r.__class__.__name__ for r in player.relics]
    print(f"Relics: {relic_names}")
    print()
    
    # Validate
    checks = [
        (player.character == "Ironclad", f"Character name: {player.character} != Ironclad"),
        (player.max_hp == 80, f"Max HP: {player.max_hp} != 80"),
        (player.energy == 3, f"Energy: {player.energy} != 3"),
        (player.gold == 99, f"Gold: {player.gold} != 99"),
        (len(player.card_manager.deck) == 10, f"Deck size: {len(player.card_manager.deck)} != 10"),
        (len(player.relics) == 1, f"Relics count: {len(player.relics)} != 1"),
        ("BurningBlood" in relic_names, f"BurningBlood not in relics: {relic_names}"),
    ]
    
    failed = [msg for passed, msg in checks if not passed]
    
    if failed:
        print("❌ FAIL:")
        for msg in failed:
            print(f"  - {msg}")
        return False
    
    print("✓ PASS: Ironclad created correctly\n")
    return True


def test_create_silent():
    """Test creating Silent player."""
    print("=" * 60)
    print("TEST 3: Create Silent Player")
    print("=" * 60)
    
    player = create_player("Silent")
    
    # Check basic properties
    print(f"Character: {player.character}")
    print(f"Max HP: {player.max_hp} (expected: 70)")
    print(f"Energy: {player.energy} (expected: 3)")
    print(f"Gold: {player.gold} (expected: 99)")
    print(f"Namespace: {player.namespace} (expected: silent)")
    print(f"Draw Count: {player.base_draw_count} (expected: 5)")
    print()
    
    # Check deck
    print(f"Deck size: {len(player.card_manager.deck)} (expected: 10)")
    deck_names = [card.__class__.__name__ for card in player.card_manager.deck]
    print(f"Deck composition: {deck_names}")
    print()
    
    # Check relics
    print(f"Relics count: {len(player.relics)} (expected: 1)")
    relic_names = [r.__class__.__name__ for r in player.relics]
    print(f"Relics: {relic_names}")
    print()
    
    # Validate
    checks = [
        (player.character == "Silent", f"Character name: {player.character} != Silent"),
        (player.max_hp == 70, f"Max HP: {player.max_hp} != 70"),
        (player.energy == 3, f"Energy: {player.energy} != 3"),
        (player.gold == 99, f"Gold: {player.gold} != 99"),
        (len(player.card_manager.deck) == 10, f"Deck size: {len(player.card_manager.deck)} != 10"),
        (len(player.relics) == 1, f"Relics count: {len(player.relics)} != 1"),
    ]
    
    failed = [msg for passed, msg in checks if not passed]
    
    if failed:
        print("❌ FAIL:")
        for msg in failed:
            print(f"  - {msg}")
        return False
    
    print("✓ PASS: Silent created correctly\n")
    return True


def test_case_insensitive():
    """Test case-insensitive character name handling."""
    print("=" * 60)
    print("TEST 4: Case-Insensitive Character Names")
    print("=" * 60)
    
    # Test different case variations
    variations = ["Ironclad", "ironclad", "IRONCLAD"]
    
    for name in variations:
        try:
            player = create_player(name)
            print(f"✓ '{name}' -> Character: {player.character}")
        except ValueError as e:
            print(f"❌ '{name}' failed: {e}")
            return False
    
    print()
    print("✓ PASS: Case-insensitive handling works\n")
    return True


def test_unknown_character():
    """Test error handling for unknown character."""
    print("=" * 60)
    print("TEST 5: Unknown Character Error Handling")
    print("=" * 60)
    
    try:
        player = create_player("NonExistentCharacter")
        print(f"❌ FAIL: Should have raised ValueError, but got {player.character}")
        return False
    except ValueError as e:
        print(f"✓ PASS: Correctly raised ValueError")
        print(f"  Error message: {e}")
        print()
        return True
    except Exception as e:
        print(f"❌ FAIL: Raised unexpected exception: {type(e).__name__}: {e}")
        return False


def main():
    """Run all tests."""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  CHARACTER SYSTEM EXTENSIBILITY TEST SUITE  ".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "═" * 58 + "╝")
    print("\n")
    
    tests = [
        ("List Characters", test_list_characters),
        ("Create Ironclad", test_create_ironclad),
        ("Create Silent", test_create_silent),
        ("Case Insensitive", test_case_insensitive),
        ("Unknown Character", test_unknown_character),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"❌ CRITICAL ERROR in {test_name}: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
        print()
    
    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print()
    print(f"Results: {passed_count}/{total_count} tests passed")
    print()
    
    if passed_count == total_count:
        print("🎉 All tests passed! Character system is working correctly.")
        return 0
    else:
        print(f"⚠️  {total_count - passed_count} test(s) failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())