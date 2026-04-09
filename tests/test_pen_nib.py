"""Test PenNib relic functionality."""
import unittest
from unittest.mock import MagicMock

from relics.global_relics.common import PenNib
from utils.types import CardType, RarityType
from actions.combat import ApplyPowerAction
from engine.game_state import game_state


class TestPenNib(unittest.TestCase):
    """Test PenNib relic: Every 10th Attack deals double damage."""

    def setUp(self):
        """Set up test fixtures."""
        self.pen_nib = PenNib()
        self.player = MagicMock()
        self.entities = []
        game_state.action_queue.clear()

    def test_pen_nib_initialization(self):
        """Test PenNib initializes correctly."""
        self.assertEqual(self.pen_nib.attacks_played, 0)
        self.assertEqual(self.pen_nib.rarity, RarityType.COMMON)

    def test_pen_nib_resets_on_combat_start(self):
        """Test attack counter resets on combat start."""
        self.pen_nib.attacks_played = 15
        self.pen_nib.on_combat_start(1)

        self.assertEqual(self.pen_nib.attacks_played, 0)
        self.assertTrue(game_state.action_queue.is_empty())

    def test_pen_nib_tracks_attacks(self):
        """Test PenNib tracks attacks played."""
        attack_card = MagicMock()
        attack_card.card_type = CardType.ATTACK

        for _ in range(5):
            self.pen_nib.on_card_play(attack_card, self.entities)

        self.assertEqual(self.pen_nib.attacks_played, 5)

    def test_pen_nib_ignores_non_attacks(self):
        """Test PenNib ignores non-attack cards."""
        skill_card = MagicMock()
        skill_card.card_type = CardType.SKILL

        self.pen_nib.on_card_play(skill_card, self.entities)

        self.assertEqual(self.pen_nib.attacks_played, 0)

    def test_pen_nib_applies_power_after_9th_attack(self):
        """Test PenNib primes the next attack after the 9th attack."""
        attack_card = MagicMock()
        attack_card.card_type = CardType.ATTACK

        for _ in range(8):
            self.pen_nib.on_card_play(attack_card, self.entities)
            self.assertTrue(game_state.action_queue.is_empty())

        self.pen_nib.on_card_play(attack_card, self.entities)
        self.assertEqual(len(game_state.action_queue.queue), 1)
        self.assertIsInstance(game_state.action_queue.queue[0], ApplyPowerAction)
        from powers.definitions.pen_nib import PenNibPower
        self.assertIsInstance(getattr(game_state.action_queue.queue[0], "power", None), PenNibPower)

    def test_pen_nib_applies_power_on_9th_and_19th_attacks(self):
        """Test PenNib primes on attacks 9, 19, 29..."""
        attack_card = MagicMock()
        attack_card.card_type = CardType.ATTACK

        for i in range(20):
            self.pen_nib.on_card_play(attack_card, self.entities)
            if (i + 1) % 10 == 9:
                self.assertEqual(len(game_state.action_queue.queue), 1)
                self.assertIsInstance(game_state.action_queue.queue[0], ApplyPowerAction)
                game_state.action_queue.clear()
            else:
                self.assertTrue(game_state.action_queue.is_empty())


if __name__ == '__main__':
    unittest.main()
