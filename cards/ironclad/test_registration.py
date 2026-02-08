#!/usr/bin/env python
"""
Test script to verify Ironclad cards are registered
"""
import sys
import os

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

# Import Ironclad package to register all cards
import cards.ironclad

# Check registry
from utils.registry import list_registered

def test_registration():
    """Test that all Ironclad cards are registered"""
    expected_cards = [
        # Starter deck
        "Ironclad.Strike",
        "Ironclad.Defend",
        "Ironclad.Bash",
        "Ironclad.Anger",
        # Common
        "Ironclad.IronWave",
        "Ironclad.PommelStrike",
        "Ironclad.HeavyBlade",
        "Ironclad.Armaments",
        "Ironclad.Flex",
        # Uncommon
        "Ironclad.Clothesline",
        "Ironclad.Inflame",
        "Ironclad.BodySlam",
        "Ironclad.Carnage",
        # Rare
        "Ironclad.Bludgeon",
        "Ironclad.LimitBreak",
        "Ironclad.Pummel",
        "Ironclad.Uppercut",
        "Ironclad.Offering",
    ]
    
    print("=" * 60)
    print("Testing Ironclad Cards Registration")
    print("=" * 60)
    
    registered_cards = list_registered("card")
    
    all_passed = True
    for card_id in expected_cards:
        if card_id in registered_cards:
            print(f"[OK] {card_id} - Registered")
        else:
            print(f"[FAIL] {card_id} - NOT registered")
            all_passed = False
    
    print("=" * 60)
    if all_passed:
        print("[OK] All Ironclad cards are registered!")
    else:
        print("[FAIL] Some Ironclad cards are not registered")
    print("=" * 60)
    
    return all_passed

if __name__ == "__main__":
    success = test_registration()
    sys.exit(0 if success else 1)
