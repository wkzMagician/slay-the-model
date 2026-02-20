"""Comprehensive tests for Flame Barrier card."""
import unittest
from tests.test_combat_utils import create_test_helper
from cards.ironclad.flame_barrier import FlameBarrier
from enemies.act1.cultist import Cultist
from utils.types import CardType, RarityType


class TestFlameBarrier(unittest.TestCase):
    def setUp(self):
        self.helper = create_test_helper()
        
    def tearDown(self):
        self.helper._reset_game_state()

    def test_basic_properties(self):
        """Test Flame Barrier has correct basic properties."""
        card = FlameBarrier()
        self.assertEqual(card.cost, 2)
        self.assertEqual(card.block, 12)
        self.assertEqual(card.card_type, CardType.POWER)
        self.assertEqual(card.rarity, RarityType.UNCOMMON)
        self.assertIn("counter_attack", card._magic)
        self.assertEqual(card._magic["counter_attack"], 4)

    def test_upgraded_properties(self):
        """Test upgraded Flame Barrier increases block and counter."""
        card = FlameBarrier()
        card.upgrade()
        self.assertEqual(card.block, 16)
        self.assertEqual(card._magic["counter_attack"], 6)

    def test_gains_block(self):
        """Test Flame Barrier gains block."""
        player = self.helper.create_player(energy=3)
        enemy = self.helper.create_enemy(Cultist)
        combat = self.helper.start_combat([enemy])
        
        initial_block = self.helper.game_state.player.block
        card = FlameBarrier()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, target=enemy)
        
        # Should gain block
        self.assertGreater(self.helper.game_state.player.block, initial_block)

    def test_applies_thorns_power(self):
        """Test Flame Barrier applies thorns power."""
        player = self.helper.create_player(energy=3)
        enemy = self.helper.create_enemy(Cultist)
        combat = self.helper.start_combat([enemy])
        
        card = FlameBarrier()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, target=enemy)
        
        # Should have a thorns/counter power applied
        powers = self.helper.game_state.player.powers
        power_names = [type(p).__name__ for p in powers]
        self.assertTrue(any("Flame" in name or "Barrier" in name or "Thorn" in name for name in power_names), 
                        f"Expected Flame Barrier power, got: {power_names}")

    def test_energy_cost(self):
        """Test Flame Barrier costs 2 energy."""
        player = self.helper.create_player(energy=3)
        enemy = self.helper.create_enemy(Cultist)
        combat = self.helper.start_combat([enemy])
        
        card = FlameBarrier()
        self.helper.add_card_to_hand(card)
        initial_energy = self.helper.game_state.player.energy
        self.helper.play_card(card, target=enemy)
        
        # Should consume 2 energy
        self.assertEqual(self.helper.game_state.player.energy, initial_energy - 2)


if __name__ == '__main__':
    unittest.main()
