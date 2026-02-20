"""Comprehensive tests for Berserk card."""
import unittest
from tests.test_combat_utils import CombatTestHelper, create_test_helper
from cards.ironclad.berserk import Berserk
from enemies.act1.cultist import Cultist
from utils.types import CardType, RarityType


class TestBerserk(unittest.TestCase):
    def setUp(self):
        self.helper = create_test_helper()

    def tearDown(self):
        self.helper._reset_game_state()

    def test_basic_properties(self):
        """Test Berserk basic properties."""
        card = Berserk()
        self.assertEqual(card.cost, 0)
        self.assertEqual(card.card_type, CardType.POWER)
        self.assertEqual(card.rarity, RarityType.RARE)
        self.assertEqual(card.damage, 0)

    def test_applies_vulnerable(self):
        """Test that Berserk applies Vulnerable to player."""
        player = self.helper.create_player()
        enemy = self.helper.create_enemy(Cultist, hp=50)
        combat = self.helper.start_combat([enemy])
        
        card = Berserk()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, target=None)
        
        # Should apply Vulnerable to player
        vulnerable_stacks = self.helper.get_power_stacks("Vulnerable")
        self.assertGreater(vulnerable_stacks, 0)

    def test_upgraded_less_vulnerable(self):
        """Test upgraded Berserk applies less Vulnerable."""
        card = Berserk()
        card.upgrade()
        self.assertEqual(card.cost, 0)
        # Upgraded version should apply 1 Vulnerable instead of 2
        self.assertEqual(card.get_magic_value("Vulnerable"), 1)

    def test_energy_cost(self):
        """Test Berserk costs 0 energy."""
        player = self.helper.create_player(energy=3)
        enemy = self.helper.create_enemy(Cultist, hp=50)
        combat = self.helper.start_combat([enemy])
        
        card = Berserk()
        self.helper.add_card_to_hand(card)
        initial_energy = self.helper.game_state.player.energy
        self.helper.play_card(card, target=None)
        
        self.assertEqual(self.helper.game_state.player.energy, initial_energy)


if __name__ == "__main__":
    unittest.main()
