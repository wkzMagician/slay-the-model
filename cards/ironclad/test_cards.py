#!/usr/bin/env python
"""
Simple test script to verify Ironclad card files exist and have correct structure
"""
import sys
import os
import ast

def test_card_structure():
    """Test that all card files have correct structure"""
    card_files = [
        # Starter deck
        "strike.py",
        "defend.py",
        "bash.py",
        "anger.py",
        # Common
        "iron_wave.py",
        "pommel_strike.py",
        "heavy_blade.py",
        "armaments.py",
        "flex.py",
        # Uncommon
        "clothesline.py",
        "severe_strike.py",
        "inflame.py",
        "body_slam.py",
        "carnage.py",
        # Rare
        "bludgeon.py",
        "limit_break.py",
        "pummel.py",
        "uppercut.py",
        "offering.py",
    ]
    
    print("=" * 60)
    print("Testing Ironclad Cards File Structure")
    print("=" * 60)
    
    all_passed = True
    cards_dir = os.path.dirname(__file__)
    
    for card_file in card_files:
        file_path = os.path.join(cards_dir, card_file)
        
        if not os.path.exists(file_path):
            print(f"[FAIL] {card_file}: File not found")
            all_passed = False
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for required imports
            required_imports = ["from cards.base import Card", "from utils.registry import register", "from utils.types import RarityType"]
            missing_imports = [imp for imp in required_imports if imp not in content]
            
            if missing_imports:
                print(f"[FAIL] {card_file}: Missing imports: {missing_imports}")
                all_passed = False
                continue
            
            # Check for @register("card") decorator
            if '@register("card")' not in content:
                print(f"[FAIL] {card_file}: Missing @register('card') decorator")
                all_passed = False
                continue
            
            # Check for class definition
            if 'class ' not in content or '(Card)' not in content:
                print(f"[FAIL] {card_file}: Missing valid class definition")
                all_passed = False
                continue
            
            # Check for required class attributes
            required_attrs = ['card_type', 'rarity', 'base_cost']
            missing_attrs = [attr for attr in required_attrs if attr not in content]
            
            if missing_attrs:
                print(f"[FAIL] {card_file}: Missing class attributes: {missing_attrs}")
                all_passed = False
                continue
            
            print(f"[OK] {card_file:20s} - File structure valid")
            
        except Exception as e:
            print(f"[FAIL] {card_file}: Error reading file - {e}")
            all_passed = False
    
    print("=" * 60)
    if all_passed:
        print("[OK] All card files have valid structure!")
    else:
        print("[FAIL] Some card files have invalid structure")
    print("=" * 60)
    
    return all_passed

if __name__ == "__main__":
    success = test_card_structure()
    sys.exit(0 if success else 1)
