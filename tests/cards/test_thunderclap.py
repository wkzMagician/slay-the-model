from entities.creature import Creature
"""Test Thunderclap - Deals damage and applies Vulnerable to ALL enemies"""
import unittest
from cards.ironclad.thunderclap import Thunderclap
from tests.test_combat_utils import CombatTestHelper

class TestThunderclap(unittest.TestCase):
    def setUp(self):
        self.helper = CombatTestHelper()
    def tearDown(self):
        self.helper._reset_game_state()

    def test_properties(self):
        card = Thunderclap()
        self.assertEqual(card.cost, 1)
        self.assertEqual(card.damage, 4)

    def test_damage(self):
        from enemies.act1.cultist import Cultist
        self.helper.create_player(max_hp=50)
        enemy = self.helper.create_enemy(Cultist, hp=100)
        self.helper.start_combat([enemy])
        card = Thunderclap()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, enemy)
        self.assertEqual(enemy.hp, 100 - 4)

    def test_vulnerable_applied(self):
        from enemies.act1.cultist import Cultist
        self.helper.create_player(max_hp=50)
        enemy = self.helper.create_enemy(Cultist, hp=100)
        self.helper.start_combat([enemy])
        card = Thunderclap()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, enemy)
        self.assertEqual(len(enemy.powers), 1)
        self.assertEqual(enemy.powers[0].__class__.__name__, "VulnerablePower")

    def test_upgraded(self):
        from enemies.act1.cultist import Cultist
        self.helper.create_player(max_hp=50)
        enemy = self.helper.create_enemy(Cultist, hp=100)
        self.helper.start_combat([enemy])
        card = Thunderclap()
        card.upgrade()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, enemy)
        self.assertEqual(enemy.hp, 100 - 7)

if __name__ == '__main__':
    unittest.main()
