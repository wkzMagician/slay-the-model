"""Simple test script for PenNib relic functionality."""
import sys
sys.path.insert(0, '.')

# Test basic imports
print("Testing basic imports...")
try:
    from powers.base import Power
    print("[OK] Power base class imported")
except Exception as e:
    print(f"[FAIL] Failed to import Power: {e}")
    sys.exit(1)

try:
    from actions.base import Action
    print("[OK] Action base class imported")
except Exception as e:
    print(f"[FAIL] Failed to import Action: {e}")
    sys.exit(1)

# Test PenNibPower
print("\nTesting PenNibPower...")
try:
    from powers.definitions.pen_nib import PenNibPower
    power = PenNibPower(amount=1, duration=1)
    print(f"[OK] PenNibPower created: {power.name}")
    print(f"  Description: {power.description}")
    print(f"  Duration: {power.duration}")
    print(f"  Multiplier: {power.damage_multiplier}")
except Exception as e:
    print(f"[FAIL] Failed to create PenNibPower: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test PenNib relic
print("\nTesting PenNib relic...")
try:
    from relics.global_relics.common import PenNib
    relic = PenNib()
    print(f"[OK] PenNib relic created")
    print(f"  Attacks played: {relic.attacks_played}")
    print(f"  Rarity: {relic.rarity.name}")
except Exception as e:
    print(f"[FAIL] Failed to create PenNib relic: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test that on_card_play works
print("\nTesting on_card_play hook...")
try:
    from cards.ironclad.strike import Strike
    from cards.ironclad.defend import Defend
    
    attack_card = Strike()
    skill_card = Defend()
    
    # Reset relic
    relic.attacks_played = 0
    
    # Play 9 attacks
    for i in range(9):
        actions = relic.on_card_play(attack_card, None, [])
        assert len(actions) == 0, f"Expected no actions, got {len(actions)}"
        assert relic.attacks_played == i + 1, f"Expected {i+1} attacks, got {relic.attacks_played}"
    
    print(f"[OK] 9 attacks tracked: {relic.attacks_played}")
    
    # 10th attack should trigger power
    actions = relic.on_card_play(attack_card, None, [])
    assert len(actions) == 1, f"Expected 1 action, got {len(actions)}"
    print(f"[OK] 10th attack triggered PenNibPower")
    
    # Check the action
    action = actions[0]
    assert hasattr(action, 'power'), "Action should have 'power' attribute"
    assert action.power == "PenNibPower", f"Expected PenNibPower, got {action.power}"
    print(f"[OK] Correct action type: {action.power}")
    
    # Test skill card doesn't count
    initial_count = relic.attacks_played
    actions = relic.on_card_play(skill_card, None, [])
    assert len(actions) == 0, "Skill card should not trigger power"
    assert relic.attacks_played == initial_count, "Skill card should not increment counter"
    print(f"[OK] Skill card correctly ignored (still {relic.attacks_played} attacks)")
    
except Exception as e:
    print(f"[FAIL] Failed on_card_play test: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test power doubles damage
print("\nTesting damage doubling...")
try:
    from entities.player import Player
    from cards.ironclad.bash import Bash
    
    player = Player(max_hp=70)
    power = PenNibPower(amount=1, duration=1, owner=player)
    
    attack_card = Bash()
    original_damage = attack_card.base_damage
    
    # Apply power
    power.on_card_play(attack_card, player, [])
    
    # Check damage was doubled
    assert attack_card.base_damage == original_damage * 2, f"Expected {original_damage*2}, got {attack_card.base_damage}"
    print(f"[OK] Damage doubled: {original_damage} -> {attack_card.base_damage}")
    
    # Check power duration is 0
    assert power.duration == 0, f"Expected duration 0, got {power.duration}"
    print(f"[OK] Power duration set to 0 (removed after use)")
    
except Exception as e:
    print(f"[FAIL] Failed damage doubling test: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*50)
print("[SUCCESS] All PenNib tests passed!")
print("="*50)
