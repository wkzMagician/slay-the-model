"""Test Sword Boomerang - Deals damage X times to random enemies"""
import unittest
from cards.ironclad.sword_boomerang import SwordBoomerang
from tests.test_combat_utils import CombatTestHelper

class TestSwordBoomerang(unittest.TestCase):
    def setUp(self):
        self.helper = CombatTestHelper()
    def tearDown(self):
        self.helper._reset_game_state()

    def test_properties(self):
        card = SwordBoomerang()
        self.assertEqual(card.cost, 1)
        self.assertEqual(card.damage, 3)

    def test_damage(self):
        from enemies.act1.cultist import Cultist
        self.helper.create_player(max_hp=50)
        enemy = self.helper.create_enemy(Cultist, hp=100)
        self.helper.start_combat([enemy])
        card = SwordBoomerang()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, enemy)
        self.assertEqual(enemy.hp, 100 - 9)  # 3 * 3 hits

    def test_upgraded(self):
        from enemies.act1.cultist import Cultist
        self.helper.create_player(max_hp=50)
        enemy = self.helper.create_enemy(Cultist, hp=100)
        self.helper.start_combat([enemy])
        card = SwordBoomerang()
        card.upgrade()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, enemy)
        self.assertEqual(enemy.hp, 100 - 16)  # 4 * 4 hits

if __name__ == '__main__':
    unittest.main()
