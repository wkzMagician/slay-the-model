from entities.creature import Creature
"""Comprehensive test for Rampage - Damage increases each play."""
import unittest
from cards.ironclad.rampage import Rampage
from tests.test_combat_utils import CombatTestHelper
from utils.types import CardType, RarityType

class TestRampage(unittest.TestCase):
    def setUp(self):
        self.helper = CombatTestHelper()
    def tearDown(self):
        self.helper._reset_game_state()

    def test_basic_properties(self):
        card = Rampage()
        self.assertEqual(card.cost, 1)
        self.assertEqual(card.damage, 8)
        self.assertEqual(card.get_magic_value("damage_gain"), 5)
        self.assertEqual(card.card_type, CardType.ATTACK)
        self.assertEqual(card.rarity, RarityType.UNCOMMON)

    def test_deals_damage(self):
        from enemies.act1.cultist import Cultist
        self.helper.create_player(max_hp=50)
        enemy = self.helper.create_enemy(Cultist, hp=100)
        self.helper.start_combat([enemy])
        card = Rampage()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, enemy)
        self.assertEqual(enemy.hp, 100 - 8)

    def test_upgraded_damage_gain(self):
        card = Rampage()
        card.upgrade()
        self.assertEqual(card.damage, 8)  # Base damage unchanged
        self.assertEqual(card.get_magic_value("damage_gain"), 8)

    def test_energy_cost(self):
        from enemies.act1.cultist import Cultist
        self.helper.create_player(max_hp=50, energy=3)
        enemy = self.helper.create_enemy(Cultist, hp=100)
        self.helper.start_combat([enemy])
        card = Rampage()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, enemy)
        from engine.game_state import game_state
        self.assertEqual(game_state.player.energy, 2)

if __name__ == '__main__':
    unittest.main()
