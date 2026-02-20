from entities.creature import Creature
"""Comprehensive test for Shockwave - Apply Weak/Vulnerable to all."""
import unittest
from cards.ironclad.shockwave import Shockwave
from tests.test_combat_utils import CombatTestHelper
from utils.types import CardType, RarityType

class TestShockwave(unittest.TestCase):
    def setUp(self):
        self.helper = CombatTestHelper()
    def tearDown(self):
        self.helper._reset_game_state()

    def test_basic_properties(self):
        card = Shockwave()
        self.assertEqual(card.cost, 2)
        self.assertEqual(card.get_magic_value("vulnerable"), 3)
        self.assertEqual(card.get_magic_value("weak"), 3)
        self.assertEqual(card.card_type, CardType.SKILL)
        self.assertEqual(card.rarity, RarityType.UNCOMMON)
        self.assertTrue(card.exhaust)

    def test_upgraded_debuffs(self):
        card = Shockwave()
        card.upgrade()
        self.assertEqual(card.get_magic_value("vulnerable"), 5)
        self.assertEqual(card.get_magic_value("weak"), 5)

    def test_energy_cost(self):
        from enemies.act1.cultist import Cultist
        self.helper.create_player(max_hp=50, energy=3)
        enemy = self.helper.create_enemy(Cultist, hp=100)
        self.helper.start_combat([enemy])
        card = Shockwave()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, enemy)
        from engine.game_state import game_state
        self.assertEqual(game_state.player.energy, 1)

if __name__ == '__main__':
    unittest.main()
