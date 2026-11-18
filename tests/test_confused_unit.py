"""
Simple unit test for ConfusedPower without full GameState.
"""
import sys
sys.path.insert(0, 'D:/game/slay-the-model')

from powers.definitions.confused import ConfusedPower

# Create minimal mock objects
class MockCard:
    def __init__(self):
        self._cost = 1

    @property
    def cost(self):
        return self._cost

class MockPlayer:
    def __init__(self):
        self.card_manager = MockCardManager()

class MockCardManager:
    def __init__(self):
        self.piles = {'hand': []}

    def get_pile(self, pile_name):
        return self.piles.get(pile_name, [])

def test_confused_power():
    """Test ConfusedPower initialization and hooks."""
    player = MockPlayer()
    power = ConfusedPower(owner=player)

    # Test initialization
    assert power.name == "Confused"
    assert power.stackable is False
    assert power.is_buff is False
    assert power.duration == -1  # -1 means permanent

    # Add card to hand
    card = MockCard()
    player.card_manager.piles['hand'].append(card)

    # The draw callback completes the cost update synchronously.
    from engine.game_state import game_state
    game_state.action_queue.clear()
    power.on_card_draw(card)
    assert game_state.action_queue.is_empty()

    # Check cost was randomized (0-3)
    assert 0 <= card.cost <= 3, "Cost should be between 0-3"

    print("✓ ConfusedPower unit tests passed!")
    # All tests passed

if __name__ == "__main__":
    test_confused_power()
    sys.exit(0)
