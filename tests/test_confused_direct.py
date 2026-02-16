"""Direct ConfusedPower test without GameState.
"""
import sys
sys.path.insert(0, 'D:/game/slay-the-model')

# Test 1: Can import ConfusedPower
try:
    from powers.definitions.confused import ConfusedPower
    power = ConfusedPower()
    assert power.name == "Confused"
    print("Test 1 PASSED: Can import ConfusedPower")
except Exception as e:
    print(f"Test 1 FAILED: {e}")
    sys.exit(1)

# Test 2: ConfusedPower has correct attributes
assert power.stackable is False, "stackable should be False"
assert power.is_buff is False, "is_buff should be False"
assert power.duration == 0, "duration should be 0"
print("Test 2 PASSED: ConfusedPower attributes")

# Test 3: on_turn_start exists and is callable
assert hasattr(power, 'on_turn_start'), "should have on_turn_start method"
assert callable(power.on_turn_start), "on_turn_start should be callable"
print("Test 3 PASSED: on_turn_start method")

print("\n=== All ConfusedPower unit tests PASSED ===")
sys.exit(0)
