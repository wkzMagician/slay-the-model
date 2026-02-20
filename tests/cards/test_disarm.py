from entities.creature import Creature
"""Comprehensive test suite for Disarm - Enemy loses Strength."""
import unittest
from cards.ironclad.disarm import Disarm
from tests.test_combat_utils import CombatTestHelper
from utils.types import CardType, RarityType


class TestDisarm(unittest.TestCase):
    def setUp(self):
        self.helper = CombatTestHelper()

    def tearDown(self):
        self.helper._reset_game_state()

    def test_basic_properties(self):
        card = Disarm()
        self.assertEqual(card.cost, 1)
        self.assertEqual(card.get_magic_value("strength_debuff"), 2)
        self.assertEqual(card.card_type, CardType.SKILL)
        self.assertEqual(card.rarity, RarityType.UNCOMMON)

    def test_applies_strength_loss(self):
        from enemies.act1.cultist import Cultist
        self.helper.create_player(max_hp=50)
        enemy = self.helper.create_enemy(Cultist, hp=100)
        self.helper.start_combat([enemy])
        card = Disarm()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, enemy)
        self.assertEqual(len(enemy.powers), 1)

    def test_energy_cost(self):
        from enemies.act1.cultist import Cultist
        self.helper.create_player(max_hp=50, energy=3)
        enemy = self.helper.create_enemy(Cultist, hp=100)
        self.helper.start_combat([enemy])
        card = Disarm()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, enemy)
        from engine.game_state import game_state
        self.assertEqual(game_state.player.energy, 2)

    def test_upgraded(self):
        card = Disarm()
        card.upgrade()
        self.assertEqual(card.get_magic_value("strength_debuff"), 3)

if __name__ == "__main__":
    unittest.main()
