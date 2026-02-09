"""
Unit tests for gold reward randomization (P1-4).
Tests gold rewards fluctuate based on enemy type.
"""
import sys
sys.path.insert(0, 'D:/game/slay-the-model')

def test_boss_gold_fluctuation():
    """Test boss gold fluctuates between 95-105."""
    from rooms.combat import CombatRoom
    from utils.types import RoomType

    # Create room without calling init
    class MockCombatRoom:
        pass

    room = MockCombatRoom()
    room.room_type = RoomType.BOSS

    gold = room._calculate_gold_reward()
    assert 95 <= gold <= 105
    print("Test 1 PASSED")
    return True

def test_elite_gold_fluctuation():
    """Test elite gold fluctuates between 25-35."""
    from rooms.combat import CombatRoom
    from utils.types import RoomType

    class MockCombatRoom:
        pass

    room = MockCombatRoom()
    room.room_type = RoomType.ELITE

    gold = room._calculate_gold_reward()
    assert 25 <= gold <= 35
    print("Test 2 PASSED")
    return True

def test_normal_gold_fluctuation():
    """Test normal gold fluctuates with random -5 to +5."""
    from rooms.combat import CombatRoom
    from utils.types import RoomType

    class MockCombatRoom:
        pass

    room = MockCombatRoom()
    room.room_type = RoomType.NORMAL

    gold = room._calculate_gold_reward()
    assert 10 <= gold <= 20
    print("Test 3 PASSED")
    return True

if __name__ == "__main__":
    try:
        test_boss_gold_fluctuation()
        test_elite_gold_fluctuation()
        test_normal_gold_fluctuation()
        print("\n=== All gold fluctuation tests PASSED ===")
        sys.exit(0)
    except Exception as e:
        print(f"FAILED: {e}")
        sys.exit(1)
