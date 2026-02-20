"""Comprehensive tests for Fire Breathing card."""
import unittest
from tests.test_combat_utils import create_test_helper
from cards.ironclad.fire_breathing import FireBreathing
from enemies.act1.cultist import Cultist
from utils.types import CardType, RarityType


class TestFireBreathing(unittest.TestCase):
    def setUp(self):
        self.helper = create_test_helper()
        
    def tearDown(self):
        self.helper._reset_game_state()

    def test_basic_properties(self):
        """Test Fire Breathing has correct basic properties."""
        card = FireBreathing()
        self.assertEqual(card.cost, 1)
        self.assertEqual(card.card_type, CardType.POWER)
        self.assertEqual(card.rarity, RarityType.UNCOMMON)
        self.assertIn("damage_on_status", card._magic)
        self.assertEqual(card._magic["damage_on_status"], 7)

    def test_upgraded_properties(self):
        """Test upgraded Fire Breathing increases damage on status."""
        card = FireBreathing()
        card.upgrade()
        self.assertEqual(card._magic["damage_on_status"], 10)

    def test_applies_power(self):
        """Test Fire Breathing applies power when played."""
        player = self.helper.create_player(energy=3)
        enemy = self.helper.create_enemy(Cultist)
        combat = self.helper.start_combat([enemy])
        
        card = FireBreathing()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, target=enemy)
        
        # Should have the power applied
        powers = self.helper.game_state.player.powers
        power_names = [type(p).__name__ for p in powers]
        self.assertTrue(any("Fire" in name or "Breathing" in name for name in power_names), 
                        f"Expected FireBreathing power, got: {power_names}")

    def test_energy_cost(self):
        """Test Fire Breathing costs 1 energy."""
        player = self.helper.create_player(energy=3)
        enemy = self.helper.create_enemy(Cultist)
        combat = self.helper.start_combat([enemy])
        
        card = FireBreathing()
        self.helper.add_card_to_hand(card)
        initial_energy = self.helper.game_state.player.energy
        self.helper.play_card(card, target=enemy)
        
        # Should consume 1 energy
        self.assertEqual(self.helper.game_state.player.energy, initial_energy - 1)


if __name__ == '__main__':
    unittest.main()
