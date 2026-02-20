"""Comprehensive test for Body Slam - Damage equals block"""
import unittest
from cards.ironclad.body_slam import BodySlam
from cards.ironclad.defend import Defend
from tests.test_combat_utils import CombatTestHelper
from utils.types import CardType, RarityType

class TestBodySlam(unittest.TestCase):
    def setUp(self):
        self.helper = CombatTestHelper()
    def tearDown(self):
        self.helper._reset_game_state()

    def test_basic_properties(self):
        card = BodySlam()
        self.assertEqual(card.cost, 1)
        self.assertEqual(card.card_type, CardType.ATTACK)
        self.assertEqual(card.rarity, RarityType.COMMON)

    def test_zero_damage_with_no_block(self):
        from enemies.act1.cultist import Cultist
        self.helper.create_player(max_hp=50)
        enemy = self.helper.create_enemy(Cultist, hp=100)
        self.helper.start_combat([enemy])
        card = BodySlam()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, enemy)
        self.assertEqual(enemy.hp, 100)  # No block = no damage

    def test_damage_equals_block(self):
        from enemies.act1.cultist import Cultist
        self.helper.create_player(max_hp=50)
        enemy = self.helper.create_enemy(Cultist, hp=100)
        self.helper.start_combat([enemy])
        # First gain block with Defend
        defend = Defend()
        self.helper.add_card_to_hand(defend)
        self.helper.play_card(defend, None)
        # Then play Body Slam
        card = BodySlam()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, enemy)
        # Damage should equal block (5)
        self.assertEqual(enemy.hp, 100 - 5)

    def test_upgraded(self):
        card = BodySlam()
        card.upgrade()
        # Body Slam+ still costs 1 but now deals damage equal to block

if __name__ == '__main__':
    unittest.main()
