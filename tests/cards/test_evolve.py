"""Comprehensive tests for Evolve card."""
import unittest
from utils.types import CardType, RarityType
from cards.ironclad.evolve import Evolve
from enemies.act1.cultist import Cultist
from tests.test_combat_utils import create_test_helper


class TestEvolve(unittest.TestCase):
    def setUp(self):
        self.helper = create_test_helper()

    def tearDown(self):
        self.helper._reset_game_state()

    def test_basic_properties(self):
        card = Evolve()
        self.assertEqual(card.cost, 1)
        self.assertEqual(card.card_type, CardType.POWER)
        self.assertEqual(card.rarity, RarityType.UNCOMMON)

    def test_applies_power(self):
        player = self.helper.create_player(energy=3)
        enemy = self.helper.create_enemy(Cultist)
        self.helper.start_combat([enemy])
        
        card = Evolve()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, target=None)
        
        # Check that Evolve power was applied
        powers = self.helper.game_state.player.powers
        power_names = [type(p).__name__ for p in powers]
        self.assertIn("EvolvePower", power_names)

    def test_energy_cost(self):
        player = self.helper.create_player(energy=3)
        enemy = self.helper.create_enemy(Cultist)
        self.helper.start_combat([enemy])
        
        card = Evolve()
        self.helper.add_card_to_hand(card)
        initial_energy = self.helper.game_state.player.energy
        self.helper.play_card(card, target=None)
        
        self.assertEqual(self.helper.game_state.player.energy, initial_energy - 1)


if __name__ == '__main__':
    unittest.main()
