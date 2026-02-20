"""
Comprehensive test suite for Iron Wave card - Block and damage.

Iron Wave: Gain 5 (upgraded: 7) block. Deal 5 (upgraded: 7) damage.
"""
import unittest
from cards.ironclad.iron_wave import IronWave
from tests.test_combat_utils import CombatTestHelper
from utils.types import CardType, RarityType


class TestIronWave(unittest.TestCase):
    """Test Iron Wave card mechanics comprehensively"""

    def setUp(self):
        self.helper = CombatTestHelper()

    def tearDown(self):
        self.helper._reset_game_state()

    def test_iron_wave_basic_properties(self):
        """Test Iron Wave has correct basic properties"""
        card = IronWave()
        self.assertEqual(card.cost, 1)
        self.assertEqual(card.damage, 5)
        self.assertEqual(card.block, 5)
        self.assertEqual(card.card_type, CardType.ATTACK)
        self.assertEqual(card.rarity, RarityType.COMMON)

    def test_iron_wave_deals_damage(self):
        """Test Iron Wave deals 5 damage"""
        from enemies.act1.cultist import Cultist
        
        self.helper.create_player(max_hp=50)
        enemy = self.helper.create_enemy(Cultist, hp=100)
        self.helper.start_combat([enemy])
        
        card = IronWave()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, enemy)
        
        self.assertEqual(enemy.hp, 100 - 5)

    def test_iron_wave_gains_block(self):
        """Test Iron Wave gains 5 block"""
        from enemies.act1.cultist import Cultist
        
        self.helper.create_player(max_hp=50)
        enemy = self.helper.create_enemy(Cultist, hp=100)
        self.helper.start_combat([enemy])
        
        card = IronWave()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, enemy)
        
        from engine.game_state import game_state
        self.assertEqual(game_state.player.block, 5)
