"""
Unit tests for P3-7: tick_down should be called by on_turn_end.
Tests that power tick_down is triggered at turn end.
"""
import sys
sys.path.insert(0, 'D:/game/slay-the-model')

from powers.base import Power

class MockCard:
    def __init__(self):
        self._cost = 1
        from utils.types import CardType
        self.card_type = CardType.ATTACK

class TestPower(Power):
    def __init__(self, duration=2):
        super().__init__(duration=duration)

def test_power_on_turn_end_calls_tick_down():
    """Test that on_turn_end calls tick_down."""
    power = TestPower(duration=2)
    owner = None

    # Call on_turn_end
    actions = power.on_turn_end()

    # Verify tick_down was called by checking duration decreased
    assert power._duration == 1, f"Duration should be decreased from 2 to 1"
    print("Test 1 PASSED: tick_down called in on_turn_end")

    return True

def test_power_tick_decreases_duration():
    """Test that tick method decreases duration."""
    power = TestPower(duration=2)

    # First tick: duration becomes 1, returns False (still > 0)
    should_remove = power.tick()
    assert should_remove is False, f"tick should return False (duration still > 0)"
    assert power._duration == 1, f"Duration should be 1 after first tick"

    # Second tick: duration becomes 0, returns True (<= 0)
    should_remove = power.tick()
    assert should_remove is True, f"tick should return True (duration reached 0)"
    assert power._duration == 0, f"Duration should be 0 after second tick"

    print("Test 2 PASSED: tick decreases duration")

    return True

if __name__ == "__main__":
    try:
        test_power_on_turn_end_calls_tick_down()
        test_power_tick_decreases_duration()
        print("\n=== All P3-7 tests PASSED ===")
        sys.exit(0)
    except AssertionError as e:
        print(f"FAILED: {e}")
        sys.exit(1)
