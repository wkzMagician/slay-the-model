"""Comprehensive tests for Rage card."""
import unittest
from tests.test_combat_utils import create_test_helper
from cards.ironclad.rage import Rage
from enemies.act1.cultist import Cultist
from utils.types import CardType, RarityType


class TestRage(unittest.TestCase):
    def setUp(self):
        self.helper = create_test_helper()

    def tearDown(self):
        self.helper._reset_game_state()

    def test_basic_properties(self):
        card = Rage()
        self.assertEqual(card.cost, 0)
        self.assertEqual(card.card_type, CardType.SKILL)
        self.assertEqual(card.rarity, RarityType.UNCOMMON)

    def test_applies_power(self):
        player = self.helper.create_player(hp=80, energy=3)
        enemy = self.helper.create_enemy(Cultist, hp=50)
        self.helper.start_combat([enemy])

        card = Rage()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, target=enemy)

        # Check that RagePower was applied
        powers = self.helper.game_state.player.powers
        power_names = [type(p).__name__ for p in powers]
        self.assertIn("RagePower", power_names)

    def test_upgraded(self):
        card = Rage()
        card.upgrade()
        # Upgrade increases block_per_attack from 3 to 5
        self.assertIn("block_per_attack", card._magic)
        self.assertEqual(card._magic["block_per_attack"], 5)

    def test_energy_cost(self):
        player = self.helper.create_player(hp=80, energy=3)
        enemy = self.helper.create_enemy(Cultist, hp=50)
        self.helper.start_combat([enemy])

        card = Rage()
        self.helper.add_card_to_hand(card)
        initial_energy = self.helper.game_state.player.energy
        self.helper.play_card(card, target=enemy)

        # Rage costs 0 energy
        self.assertEqual(self.helper.game_state.player.energy, initial_energy)


if __name__ == "__main__":
    unittest.main()
