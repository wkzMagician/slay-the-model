"""
Simple unit tests for P3-7: tick_down behavior.
"""
import sys
sys.path.insert(0, 'D:/game/slay-the-model')

from powers.base import Power

class TestPower(Power):
    def __init__(self, duration=2):
        super().__init__(duration=duration)

def test_tick_simple():
    """Test that tick decreases duration correctly."""
    power = TestPower(duration=2)
    
    # First tick: duration becomes 1
    should_remove = power.tick()
    assert should_remove is False
    assert power._duration == 1
    
    # Second tick: duration becomes 0
    should_remove = power.tick()
    assert should_remove is True
    assert power._duration == 0
