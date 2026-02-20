"""Comprehensive tests for Bloodletting card."""
import unittest
from tests.test_combat_utils import CombatTestHelper, create_test_helper
from cards.ironclad.bloodletting import Bloodletting
from enemies.act1.cultist import Cultist
from utils.types import CardType, RarityType


class TestBloodletting(unittest.TestCase):
    def setUp(self):
        self.helper = create_test_helper()

    def tearDown(self):
        self.helper._reset_game_state()

    def test_basic_properties(self):
        """Test Bloodletting basic properties."""
        card = Bloodletting()
        self.assertEqual(card.cost, 0)
        self.assertEqual(card.card_type, CardType.SKILL)
        self.assertEqual(card.rarity, RarityType.UNCOMMON)
        self.assertEqual(card.damage, 0)

    def test_gains_energy(self):
        """Test that Bloodletting gains energy."""
        player = self.helper.create_player(energy=3, max_energy=5)  # max_energy=5 allows +2 gain
        enemy = self.helper.create_enemy(Cultist, hp=50)
        combat = self.helper.start_combat([enemy])
        
        initial_energy = self.helper.game_state.player.energy
        card = Bloodletting()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, target=None)
        
        # Should gain 2 energy (net +2 after 0 cost)
        self.assertGreaterEqual(self.helper.game_state.player.energy, initial_energy + 2)

    def test_loses_hp(self):
        """Test that Bloodletting costs HP."""
        player = self.helper.create_player(hp=80)
        enemy = self.helper.create_enemy(Cultist, hp=50)
        combat = self.helper.start_combat([enemy])
        
        initial_hp = self.helper.get_player_hp()
        card = Bloodletting()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, target=None)
        
        # Should lose 2 HP
        self.assertEqual(self.helper.get_player_hp(), initial_hp - 2)

    def test_upgraded_more_energy(self):
        """Test upgraded Bloodletting gains more energy."""
        card = Bloodletting()
        card.upgrade()
        self.assertEqual(card.cost, 0)
        self.assertEqual(card.energy_gain, 3)

    def test_energy_cost(self):
        """Test Bloodletting costs 0 energy."""
        player = self.helper.create_player(energy=3, max_energy=5)  # max_energy=5 allows +2 gain
        enemy = self.helper.create_enemy(Cultist, hp=50)
        combat = self.helper.start_combat([enemy])
        
        card = Bloodletting()
        self.helper.add_card_to_hand(card)
        initial_energy = self.helper.game_state.player.energy
        self.helper.play_card(card, target=None)
        
        # Net energy gain = +2 (0 cost + 2 gain)
        self.assertEqual(self.helper.game_state.player.energy, initial_energy + 2)


if __name__ == "__main__":
    unittest.main()
