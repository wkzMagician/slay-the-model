"""Comprehensive test for Uppercut - Damage + Vulnerable + Weak."""
import unittest
from cards.ironclad.uppercut import Uppercut
from tests.test_combat_utils import CombatTestHelper
from utils.types import CardType, RarityType

class TestUppercut(unittest.TestCase):
    def setUp(self):
        self.helper = CombatTestHelper()
    def tearDown(self):
        self.helper._reset_game_state()

    def test_basic_properties(self):
        card = Uppercut()
        self.assertEqual(card.cost, 2)
        self.assertEqual(card.damage, 13)
        self.assertEqual(card.get_magic_value("vulnerable"), 1)
        self.assertEqual(card.get_magic_value("weak"), 1)
        self.assertEqual(card.card_type, CardType.ATTACK)
        self.assertEqual(card.rarity, RarityType.UNCOMMON)

    def test_deals_damage(self):
        from enemies.act1.cultist import Cultist
        self.helper.create_player(max_hp=50)
        enemy = self.helper.create_enemy(Cultist, hp=100)
        self.helper.start_combat([enemy])
        card = Uppercut()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, enemy)
        self.assertEqual(enemy.hp, 100 - 13)

    def test_upgraded_debuffs(self):
        card = Uppercut()
        card.upgrade()
        self.assertEqual(card.damage, 13)  # Damage unchanged
        self.assertEqual(card.get_magic_value("vulnerable"), 2)
        self.assertEqual(card.get_magic_value("weak"), 2)

    def test_energy_cost(self):
        from enemies.act1.cultist import Cultist
        self.helper.create_player(max_hp=50, energy=3)
        enemy = self.helper.create_enemy(Cultist, hp=100)
        self.helper.start_combat([enemy])
        card = Uppercut()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, enemy)
        from engine.game_state import game_state
        self.assertEqual(game_state.player.energy, 1)

if __name__ == '__main__':
    unittest.main()
