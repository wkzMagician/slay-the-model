from entities.creature import Creature
"""
Test suite for Clothesline card - Attack that applies Weak debuff.

Clothesline: Deal 12 (upgraded: 14) damage and apply Weak 2 (upgraded: 3).
Weak: When affected creature attacks, deals 25% less damage.
"""

import unittest
from cards.ironclad.clothesline import Clothesline
from tests.test_combat_utils import CombatTestHelper


class TestClothesline(unittest.TestCase):
    """Test Clothesline card mechanics"""

    def setUp(self):
        """Set up test fixtures"""
        self.helper = CombatTestHelper()

    def tearDown(self):
        """Clean up after tests"""
        self.helper._reset_game_state()

    def test_clothesline_basic_properties(self):
        """Test Clothesline has correct basic properties"""
        card = Clothesline()
        
        # Check display name
        self.assertEqual(str(card.display_name), "Clothesline")
        
        # Check cost
        self.assertEqual(card.cost, 2)
        
        # Check damage (non-upgraded)
        self.assertEqual(card.damage, 12)
        
        # Check weak amount (base: 2)
        self.assertEqual(card.get_magic_value("weak"), 2)

    def test_clothesline_deals_damage(self):
        """Test Clothesline deals damage to target"""
        from enemies.act1.cultist import Cultist
        
        self.helper.create_player(max_hp=50)
        enemy = self.helper.create_enemy(Cultist, hp=100)
        combat = self.helper.start_combat([enemy])
        
        # Create and add Clothesline to hand, then play
        clothesline = Clothesline()
        self.helper.add_card_to_hand(clothesline)
        self.helper.play_card(clothesline, enemy)
        
        # Check enemy took damage
        self.assertEqual(enemy.hp, 100 - 12)

    def test_clothesline_applies_weak(self):
        """Test Clothesline applies Weak debuff"""
        from enemies.act1.cultist import Cultist
        from powers.definitions.weak import WeakPower
        
        self.helper.create_player(max_hp=50)
        enemy = self.helper.create_enemy(Cultist, hp=100)
        combat = self.helper.start_combat([enemy])
        
        # Create and add Clothesline to hand, then play
        clothesline = Clothesline()
        self.helper.add_card_to_hand(clothesline)
        self.helper.play_card(clothesline, enemy)
        
        # Check enemy has Weak power (check enemy.powers directly)
        self.assertEqual(len(enemy.powers), 1)
        weak_power = enemy.powers[0]
        self.assertEqual(weak_power.__class__.__name__, "WeakPower")
        self.assertEqual(weak_power.amount, 2)

    def test_clothesline_upgraded_damage(self):
        """Test upgraded Clothesline deals 14 damage"""
        from enemies.act1.cultist import Cultist
        
        self.helper.create_player(max_hp=50)
        enemy = self.helper.create_enemy(Cultist, hp=100)
        combat = self.helper.start_combat([enemy])
        
        # Create, upgrade, add to hand, then play Clothesline
        clothesline = Clothesline()
        clothesline.upgrade()  # Damage: 12 -> 14
        self.helper.add_card_to_hand(clothesline)
        self.helper.play_card(clothesline, enemy)
        
        # Check enemy took upgraded damage
        self.assertEqual(enemy.hp, 100 - 14)

    def test_clothesline_upgraded_weak(self):
        """Test upgraded Clothesline applies Weak 3"""
        from enemies.act1.cultist import Cultist
        
        self.helper.create_player(max_hp=50)
        enemy = self.helper.create_enemy(Cultist, hp=100)
        combat = self.helper.start_combat([enemy])
        
        # Create, upgrade, add to hand, then play Clothesline
        clothesline = Clothesline()
        clothesline.upgrade()  # Weak: 2 -> 3
        self.helper.add_card_to_hand(clothesline)
        self.helper.play_card(clothesline, enemy)
        
        # Check enemy has upgraded Weak amount (check enemy.powers directly)
        self.assertEqual(len(enemy.powers), 1)
        weak_power = enemy.powers[0]
        self.assertEqual(weak_power.__class__.__name__, "WeakPower")
        self.assertEqual(weak_power.amount, 3)


if __name__ == '__main__':
    unittest.main()
