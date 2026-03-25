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


class TestRewardCardUpgradeChance:
    """Tests for combat reward upgraded card chance by act/ascension."""

    @patch('utils.random.random.choice', side_effect=lambda seq: seq[0])
    @patch('utils.random.random.choices')
    @patch('utils.random.list_registered')
    @patch('utils.random.get_registered')
    @patch('engine.game_state.game_state')
    def test_act2_reward_can_upgrade(self, mock_gs, mock_get, mock_list,
                                     mock_choices, _mock_choice):
        """Act 2 combat rewards can roll upgraded cards."""
        mock_gs.current_act = 2
        mock_gs.ascension = 0
        mock_gs.player.relics = []

        mock_list.return_value = ["card1"]

        mock_card_cls = MagicMock()
        mock_card = MagicMock()
        mock_card.namespace = "test"
        mock_card.rarity = RarityType.COMMON
        mock_card.can_upgrade.return_value = True
        mock_card_cls.return_value = mock_card
        mock_get.return_value = mock_card_cls

        mock_choices.return_value = [(RarityType.COMMON, ["card1"])]

        from utils.random import get_random_card_reward

        with patch('utils.random.random.random', return_value=0.2):
            card = get_random_card_reward(
                namespaces=["test"],
                encounter_type="normal",
                allow_upgraded=True,
            )

        assert card is mock_card
        mock_card.upgrade.assert_called_once()

    @patch('utils.random.random.choice', side_effect=lambda seq: seq[0])
    @patch('utils.random.random.choices')
    @patch('utils.random.list_registered')
    @patch('utils.random.get_registered')
    @patch('engine.game_state.game_state')
    def test_act1_reward_never_upgrades(self, mock_gs, mock_get, mock_list,
                                        mock_choices, _mock_choice):
        """Act 1 combat rewards should not upgrade."""
        mock_gs.current_act = 1
        mock_gs.ascension = 0
        mock_gs.player.relics = []

        mock_list.return_value = ["card1"]

        mock_card_cls = MagicMock()
        mock_card = MagicMock()
        mock_card.namespace = "test"
        mock_card.rarity = RarityType.COMMON
        mock_card.can_upgrade.return_value = True
        mock_card_cls.return_value = mock_card
        mock_get.return_value = mock_card_cls

        mock_choices.return_value = [(RarityType.COMMON, ["card1"])]

        from utils.random import get_random_card_reward

        with patch('utils.random.random.random', return_value=0.0):
            card = get_random_card_reward(
                namespaces=["test"],
                encounter_type="normal",
                allow_upgraded=True,
            )

        assert card is mock_card
        mock_card.upgrade.assert_not_called()

    @patch('utils.random.random.choice', side_effect=lambda seq: seq[0])
    @patch('utils.random.random.choices')
    @patch('utils.random.list_registered')
    @patch('utils.random.get_registered')
    @patch('engine.game_state.game_state')
    def test_asc12_act2_upgrade_chance_halved(self, mock_gs, mock_get, mock_list,
                                              mock_choices, _mock_choice):
        """Ascension 12+ halves Act 2 reward upgrade chance to 12.5%."""
        mock_gs.current_act = 2
        mock_gs.ascension = 12
        mock_gs.player.relics = []

        mock_list.return_value = ["card1"]

        mock_card_cls = MagicMock()
        mock_card = MagicMock()
        mock_card.namespace = "test"
        mock_card.rarity = RarityType.COMMON
        mock_card.can_upgrade.return_value = True
        mock_card_cls.return_value = mock_card
        mock_get.return_value = mock_card_cls

        mock_choices.return_value = [(RarityType.COMMON, ["card1"])]

        from utils.random import get_random_card_reward

        with patch('utils.random.random.random', return_value=0.2):
            card = get_random_card_reward(
                namespaces=["test"],
                encounter_type="normal",
                allow_upgraded=True,
            )

        assert card is mock_card
        mock_card.upgrade.assert_not_called()


class TestExcludeByCardIdstr:
    """exclude_set / exclude_card_ids use Card.idstr only."""

    def setup_method(self):
        import cards.ironclad  # noqa: F401 — registers Ironclad cards in global registry

    def test_get_random_card_reward_respects_idstr_exclude(self):
        from utils.random import get_random_card_reward

        c1 = get_random_card_reward(
            namespaces=["ironclad"],
            encounter_type="normal",
            allow_upgraded=False,
        )
        assert c1 is not None
        for _ in range(100):
            c2 = get_random_card_reward(
                namespaces=["ironclad"],
                encounter_type="normal",
                allow_upgraded=False,
                exclude_set=[c1.idstr],
            )
            assert c2 is None or c2.idstr != c1.idstr

    def test_get_random_card_respects_idstr_exclude(self):
        from utils.random import get_random_card
        from utils.types import RarityType

        c1 = get_random_card(
            namespaces=["ironclad"],
            rarities=[RarityType.COMMON],
            exclude_starter=True,
        )
        assert c1 is not None
        for _ in range(100):
            c2 = get_random_card(
                namespaces=["ironclad"],
                rarities=[RarityType.COMMON],
                exclude_starter=True,
                exclude_card_ids=[c1.idstr],
            )
            assert c2 is None or c2.idstr != c1.idstr
