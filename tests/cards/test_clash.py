"""
Comprehensive test suite for Clash card - High damage attack.

Clash: Deal 14 (upgraded: 18) damage. Can only be played if ALL cards in hand are Attacks.
"""
import unittest
from cards.ironclad.clash import Clash
from tests.test_combat_utils import CombatTestHelper
from utils.types import CardType, RarityType


class TestClash(unittest.TestCase):
    """Test Clash card mechanics comprehensively"""

    def setUp(self):
        self.helper = CombatTestHelper()

    def tearDown(self):
        self.helper._reset_game_state()

    def test_clash_basic_properties(self):
        """Test Clash has correct basic properties"""
        card = Clash()
        self.assertEqual(card.cost, 0)
        self.assertEqual(card.damage, 14)
        self.assertEqual(card.card_type, CardType.ATTACK)
        self.assertEqual(card.rarity, RarityType.COMMON)

    def test_clash_deals_damage(self):
        """Test Clash deals 14 damage to target"""
        from enemies.act1.cultist import Cultist
        
        self.helper.create_player(max_hp=50)
        enemy = self.helper.create_enemy(Cultist, hp=100)
        self.helper.start_combat([enemy])
        
        card = Clash()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, enemy)
        
        self.assertEqual(enemy.hp, 100 - 14)

    def test_clash_zero_energy_cost(self):
        """Test Clash costs 0 energy"""
        from enemies.act1.cultist import Cultist
        
        self.helper.create_player(max_hp=50, energy=3)
        enemy = self.helper.create_enemy(Cultist, hp=100)
        self.helper.start_combat([enemy])
        
        card = Clash()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, enemy)
        
        from engine.game_state import game_state
        self.assertEqual(game_state.player.energy, 3)

    def test_clash_upgraded_damage(self):
        """Test upgraded Clash deals 18 damage"""
        from enemies.act1.cultist import Cultist
        
        self.helper.create_player(max_hp=50)
        enemy = self.helper.create_enemy(Cultist, hp=100)
        self.helper.start_combat([enemy])
        
        card = Clash()
        card.upgrade()
        self.assertEqual(card.damage, 18)
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, enemy)
        
        self.assertEqual(enemy.hp, 100 - 18)

    def test_clash_kills_enemy(self):
        """Test Clash can kill low HP enemy (14 damage)"""
        from enemies.act1.cultist import Cultist
        
        self.helper.create_player(max_hp=50)
        enemy = self.helper.create_enemy(Cultist, hp=14)
        self.helper.start_combat([enemy])
        
        card = Clash()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, enemy)
        
        # Enemy with 14 HP should die after 14 damage
        self.assertLessEqual(enemy.hp, 0)

    # todo: test can_play: unplayable when skill cards at hand

if __name__ == '__main__':
    unittest.main()
