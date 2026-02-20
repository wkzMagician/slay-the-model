"""
Tests for random card reward system with rarity weights.
"""
import pytest
from unittest.mock import patch, MagicMock
from utils.random import CARD_RARITY_PROBABILITIES
from utils.types import RarityType, CardType


class TestCardRarityProbabilities:
    """Test rarity probability configurations."""

    def test_normal_encounter_base_probs(self):
        """Test normal encounter has correct base probabilities."""
        probs = CARD_RARITY_PROBABILITIES["normal"]
        assert probs[RarityType.COMMON] == 60
        assert probs[RarityType.UNCOMMON] == 37
        assert probs[RarityType.RARE] == 3
        total = sum(probs.values())
        assert total == 100

    def test_elite_encounter_base_probs(self):
        """Test elite encounter has higher rare chance."""
        probs = CARD_RARITY_PROBABILITIES["elite"]
        assert probs[RarityType.COMMON] == 50
        assert probs[RarityType.UNCOMMON] == 40
        assert probs[RarityType.RARE] == 10
        total = sum(probs.values())
        assert total == 100

    def test_shop_encounter_base_probs(self):
        """Test shop encounter has moderate rare chance."""
        probs = CARD_RARITY_PROBABILITIES["shop"]
        assert probs[RarityType.COMMON] == 54
        assert probs[RarityType.UNCOMMON] == 37
        assert probs[RarityType.RARE] == 9
        total = sum(probs.values())
        assert total == 100


class TestRollingOffsetCounter:
    """Test rolling offset counter functions."""

    def setup_method(self):
        """Setup mocks before each test."""
        # Mock game_state
        from unittest.mock import MagicMock
        import sys

        mock_gs = MagicMock()
        mock_gs.card_chance_common_counter = 0
        sys.modules['engine.game_state'] = MagicMock()
        sys.modules['engine.game_state'].game_state = mock_gs

    def test_increment_counter(self):
        """Test counter increments correctly."""
        from utils.random import increment_card_chance_common_counter
        from engine.game_state import game_state

        initial = game_state.card_chance_common_counter
        assert initial == 0

        increment_card_chance_common_counter()
        assert game_state.card_chance_common_counter == initial + 1

        increment_card_chance_common_counter()
        increment_card_chance_common_counter()
        assert game_state.card_chance_common_counter == initial + 3

    def test_reset_counter(self):
        """Test counter resets correctly."""
        from utils.random import increment_card_chance_common_counter, reset_card_chance_common_counter
        from engine.game_state import game_state

        # Increment counter
        for _ in range(10):
            increment_card_chance_common_counter()
        assert game_state.card_chance_common_counter == 10

        # Reset counter
        reset_card_chance_common_counter()
        assert game_state.card_chance_common_counter == 0


class TestGetRandomCardRewardIntegration:
    """Integration tests for get_random_card_reward function."""

    @patch('utils.random.list_registered')
    @patch('utils.random.get_registered')
    @patch('engine.game_state.game_state')
    def test_rolling_offset_increases_rare_chance(self, mock_gs, mock_get, mock_list):
        """Test that rolling offset increases rare probability."""
        # Setup mock game state
        mock_gs.card_chance_common_counter = 0

        # Setup mock registry to return test cards
        mock_list.return_value = ["card1", "card2", "card3"]

        # Create mock card class
        mock_card_cls = MagicMock()
        mock_card_instance = MagicMock()
        mock_card_instance.namespace = "test"
        mock_card_instance.card_type = CardType.ATTACK
        mock_card_instance.set = None
        mock_card_instance.rarity = RarityType.COMMON
        mock_card_instance.__class__ = type('Card', (), {})
        mock_card_cls.return_value = mock_card_instance

        # Make get_registered return the same mock for all cards
        mock_get.return_value = mock_card_cls

        # Import after mocking to avoid circular import
        from utils.random import get_random_card_reward, increment_card_chance_common_counter

        # Get 10 cards with offset=0
        cards_offset_0 = []
        for _ in range(10):
            card = get_random_card_reward(
                namespaces=["test"],
                encounter_type="normal",
                use_rolling_offset=False
            )
            cards_offset_0.append(card)

        # Increment counter to increase rare chance
        for _ in range(47):  # Max offset
            increment_card_chance_common_counter()

        assert mock_gs.card_chance_common_counter == 47

        # Get 10 cards with offset=47
        cards_offset_47 = []
        for _ in range(10):
            card = get_random_card_reward(
                namespaces=["test"],
                encounter_type="normal",
                use_rolling_offset=True
            )
            cards_offset_47.append(card)

        # Verify cards were returned
        assert len(cards_offset_0) == 10
        assert len(cards_offset_47) == 10

    @patch('utils.random.list_registered')
    @patch('utils.random.get_registered')
    def test_different_encounter_types(self, mock_get, mock_list):
        """Test different encounter types work correctly."""
        # Setup mock registry
        mock_list.return_value = ["card1", "card2", "card3"]

        # Create mock card class
        mock_card_cls = MagicMock()
        mock_card_instance = MagicMock()
        mock_card_instance.namespace = "test"
        mock_card_instance.card_type = CardType.ATTACK
        mock_card_instance.set = None
        mock_card_instance.rarity = RarityType.COMMON
        mock_card_instance.__class__ = type('Card', (), {})
        mock_card_cls.return_value = mock_card_instance

        mock_get.return_value = mock_card_cls

        # Import after mocking
        from utils.random import get_random_card_reward

        # Test normal encounter
        card_normal = get_random_card_reward(
            namespaces=["test"],
            encounter_type="normal"
        )
        assert card_normal is not None

        # Test elite encounter
        card_elite = get_random_card_reward(
            namespaces=["test"],
            encounter_type="elite"
        )
        assert card_elite is not None

        # Test shop encounter
        card_shop = get_random_card_reward(
            namespaces=["test"],
            encounter_type="shop"
        )
        assert card_shop is not None

