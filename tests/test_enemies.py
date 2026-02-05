"""
Unit tests for Enemy entities.
"""
import unittest

from entities.enemies import Cultist, JawWorm, FungalBeast, Sentry, Slaver


class TestEnemies(unittest.TestCase):
    """Test suite for Enemy implementations."""
    
    def test_cultist_weak(self):
        """Test Cultist is weak enemy."""
        enemy = Cultist()
        self.assertEqual(enemy.name, "Cultist")
        self.assertEqual(enemy.max_hp, 24)
        self.assertEqual(enemy.damage, 6)
        self.assertTrue(enemy.is_elite is False)
        self.assertTrue(enemy.is_boss is False)
        self.assertTrue(enemy.weak)  # Cultists are weak
        
    def test_jaw_worm_fast_weak(self):
        """Test Jaw Worm is fast weak enemy."""
        enemy = JawWorm()
        self.assertEqual(enemy.name, "Jaw Worm")
        self.assertEqual(enemy.max_hp, 28)
        self.assertEqual(enemy.damage, 5)
        self.assertTrue(enemy.is_elite is False)
        self.assertTrue(enemy.is_boss is False)
        self.assertTrue(enemy.weak)  # Jaw Worms are weak
        
    def test_fungal_beast_medium(self):
        """Test Fungal Beast is medium enemy."""
        enemy = FungalBeast()
        self.assertEqual(enemy.name, "Fungal Beast")
        self.assertEqual(enemy.max_hp, 42)
        self.assertEqual(enemy.damage, 8)
        self.assertTrue(enemy.is_elite is False)
        self.assertTrue(enemy.is_boss is False)
        self.assertFalse(enemy.weak)  # Standard enemy, no weak modifier
        
    def test_sentry_strong_elite(self):
        """Test Sentry is strong elite enemy."""
        enemy = Sentry()
        self.assertEqual(enemy.name, "Sentry")
        self.assertEqual(enemy.max_hp, 82)
        self.assertEqual(enemy.damage, 12)
        self.assertTrue(enemy.is_elite is True)
        self.assertTrue(enemy.is_boss is False)
        self.assertFalse(enemy.weak)  # Elite enemies are not weak
        self.assertEqual(enemy.strength, 2)  # Sentry has strength bonus
        
    def test_slaver_boss_strong(self):
        """Test Slaver is strong boss enemy."""
        enemy = Slaver()
        self.assertEqual(enemy.name, "Slaver")
        self.assertEqual(enemy.max_hp, 250)
        self.assertEqual(enemy.damage, 18)
        self.assertTrue(enemy.is_elite is False)
        self.assertTrue(enemy.is_boss is True)
        self.assertFalse(enemy.weak)  # Boss enemies are not weak
        self.assertEqual(enemy.strength, 4)  # Slaver has strength bonus
        self.assertEqual(enemy.artifact, 3)  # Boss has artifact damage reduction
        
    def test_enemy_damage_calculation(self):
        """Test enemy damage calculation with modifiers."""
        enemy = Sentry()
        
        # Test normal damage
        initial_hp = enemy.current_hp
        damage = enemy.take_damage(10, source="test")
        self.assertEqual(damage, 10)
        self.assertEqual(enemy.current_hp, initial_hp - 10)
        
        # Reset and test damage
        enemy.reset_for_combat()
        damage = enemy.take_damage(10, source="test")
        # Sentry: strength doesn't affect incoming damage
        self.assertEqual(damage, 10)
        self.assertEqual(enemy.current_hp, enemy.max_hp - 10)
        
    def test_enemy_death(self):
        """Test enemy death state."""
        enemy = FungalBeast()  # Use non-weak enemy for simpler test (42 HP)
        self.assertFalse(enemy.is_dead)
        
        # Take lethal damage
        enemy.take_damage(50, source="test")
        self.assertTrue(enemy.is_dead)
        self.assertEqual(enemy.current_hp, 0)
        
    def test_enemy_reset(self):
        """Test enemy reset for new combat."""
        enemy = FungalBeast()  # 42 HP
        
        # Take lethal damage (enough to kill)
        enemy.take_damage(50, source="test")
        self.assertTrue(enemy.is_dead)
        
        # Reset
        enemy.reset_for_combat()
        self.assertFalse(enemy.is_dead)  # Property access
        self.assertEqual(enemy.current_hp, enemy.max_hp)


if __name__ == "__main__":
    unittest.main()
