from entities.creature import Creature
"""
Comprehensive test suite for Strike card - Basic attack.

Strike: Deal 6 (upgraded: 9) damage. Cost 1 energy.
"""
import unittest
from cards.ironclad.strike import Strike
from tests.test_combat_utils import CombatTestHelper
from utils.types import CardType, RarityType


class TestStrike(unittest.TestCase):
    """Test Strike card mechanics comprehensively"""

    def setUp(self):
        self.helper = CombatTestHelper()

    def tearDown(self):
        self.helper._reset_game_state()

    def test_strike_basic_properties(self):
        """Test Strike has correct basic properties"""
        card = Strike()
        self.assertEqual(card.cost, 1)
        self.assertEqual(card.damage, 6)
        self.assertEqual(card.card_type, CardType.ATTACK)
        self.assertEqual(card.rarity, RarityType.STARTER)
        self.assertEqual(card.attack_times, 1)

    def test_strike_deals_damage(self):
        """Test Strike deals 6 damage to target"""
        from enemies.act1.cultist import Cultist
        
        self.helper.create_player(max_hp=50)
        enemy = self.helper.create_enemy(Cultist, hp=100)
        self.helper.start_combat([enemy])
        
        card = Strike()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, enemy)
        
        self.assertEqual(enemy.hp, 100 - 6)

    def test_strike_energy_cost(self):
        """Test Strike costs 1 energy"""
        from enemies.act1.cultist import Cultist
        
        self.helper.create_player(max_hp=50, energy=3)
        enemy = self.helper.create_enemy(Cultist, hp=100)
        self.helper.start_combat([enemy])
        
        card = Strike()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, enemy)
        
        # Player should have 2 energy left (3-1)
        from engine.game_state import game_state
        self.assertEqual(game_state.player.energy, 2)

    def test_strike_insufficient_energy(self):
        """Test Strike cannot be played with 0 energy"""
        from enemies.act1.cultist import Cultist
        
        self.helper.create_player(max_hp=50, energy=0)
        enemy = self.helper.create_enemy(Cultist, hp=100)
        self.helper.start_combat([enemy])
        
        card = Strike()
        self.helper.add_card_to_hand(card)
        
        # Check can_play returns False
        can_play, reason = card.can_play()
        self.assertFalse(can_play)

    def test_strike_upgraded_damage(self):
        """Test upgraded Strike deals 9 damage"""
        from enemies.act1.cultist import Cultist
        
        self.helper.create_player(max_hp=50)
        enemy = self.helper.create_enemy(Cultist, hp=100)
        self.helper.start_combat([enemy])
        
        card = Strike()
        card.upgrade()
        self.assertEqual(card.damage, 9)
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, enemy)
        
        self.assertEqual(enemy.hp, 100 - 9)

    def test_strike_multiple_in_deck(self):
        """Test playing multiple Strike cards"""
        from enemies.act1.cultist import Cultist
        
        self.helper.create_player(max_hp=50, energy=3)
        enemy = self.helper.create_enemy(Cultist, hp=100)
        self.helper.start_combat([enemy])
        
        # Play 2 Strikes
        for i in range(2):
            card = Strike()
            self.helper.add_card_to_hand(card)
            self.helper.play_card(card, enemy)
        
        # 6 * 2 = 12 damage
        self.assertEqual(enemy.hp, 100 - 12)


if __name__ == '__main__':
    unittest.main()
