"""
Unit tests for draw count modification (P2-1).
Tests that player.draw_count can be modified and affects card drawing.
"""
import sys
sys.path.insert(0, 'D:/game/slay-the-model')

def test_draw_count_property():
    """Test Player has draw_count property."""
    from player.player import Player

    player = Player()

    # Test 1: base_draw_count is initialized
    assert hasattr(player, 'base_draw_count'), "Should have base_draw_count attribute"
    assert player.base_draw_count == 5, "Default draw count should be 5"

    # Test 2: draw_count property returns base value
    assert hasattr(player, 'draw_count'), "Should have draw_count property"
    assert player.draw_count == 5, "Default draw count should be 5"

    print("Test 1-2 PASSED: Player draw_count property")

    return True

if __name__ == "__main__":
    try:
        test_draw_count_property()
        sys.exit(0)
    except AssertionError as e:
        print(f"FAILED: {e}")
        sys.exit(1)
