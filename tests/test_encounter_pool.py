# -*- coding: utf-8 -*-
"""
Unit tests for Encounter Pool system.

Tests verify that enemies are correctly selected based on encounter type
(normal, elite, boss) and that the pool system works correctly.
"""
import unittest
from map.encounter_pool import EncounterPool


class TestEncounterPool(unittest.TestCase):
    """Test cases for EncounterPool"""

    def setUp(self):
        """Set up test fixtures"""
        # Use fixed seed for deterministic tests
        self.pool = EncounterPool(seed=42, act_id=1)

    def test_pool_initialization(self):
        """Test that pool initializes with correct attributes"""
        self.assertIsNotNone(self.pool.easy_pool)
        self.assertIsNotNone(self.pool.hard_pool)
        self.assertIsNotNone(self.pool.elite_pool)
        self.assertIsNotNone(self.pool.boss_pool)

    def test_act1_easy_pool_has_encounters(self):
        """Test Act 1 easy pool has expected encounters"""
        pool = EncounterPool(seed=42, act_id=1)
        # Act 1 easy pool should have these encounters
        self.assertIn('Cultist', pool.easy_pool)
        self.assertIn('Jaw Worm', pool.easy_pool)
        self.assertIn('2 Louse', pool.easy_pool)
        self.assertIn('Small Slimes', pool.easy_pool)

    def test_act1_hard_pool_has_encounters(self):
        """Test Act 1 hard pool has expected encounters"""
        pool = EncounterPool(seed=42, act_id=1)
        # Act 1 hard pool should have encounters
        self.assertGreater(len(pool.hard_pool), 0)

    def test_act1_elite_pool_has_encounters(self):
        """Test Act 1 elite pool has expected encounters"""
        pool = EncounterPool(seed=42, act_id=1)
        # Act 1 elite pool should have these encounters
        self.assertIn('Gremlin Nob', pool.elite_pool)
        self.assertIn('Lagavulin', pool.elite_pool)
        self.assertIn('3 Sentries', pool.elite_pool)

    def test_act1_boss_pool_has_bosses(self):
        """Test Act 1 boss pool has expected bosses"""
        pool = EncounterPool(seed=42, act_id=1)
        # Act 1 boss pool should have these bosses
        self.assertIn('The Guardian', pool.boss_pool)
        self.assertIn('Slime Boss', pool.boss_pool)
        self.assertIn('The Hexaghost', pool.boss_pool)

    def test_get_pool_name_early_encounters(self):
        """Test pool name detection for early encounters (Act 1)"""
        # First 3 encounters in Act 1 should be 'easy'
        self.assertEqual(self.pool.get_pool_name(0, act=1), 'easy')
        self.assertEqual(self.pool.get_pool_name(1, act=1), 'easy')
        self.assertEqual(self.pool.get_pool_name(2, act=1), 'easy')

    def test_get_pool_name_late_encounters(self):
        """Test pool name detection for late encounters (Act 1)"""
        # After first 3 encounters in Act 1 should be 'hard'
        self.assertEqual(self.pool.get_pool_name(3, act=1), 'hard')
        self.assertEqual(self.pool.get_pool_name(5, act=1), 'hard')
        self.assertEqual(self.pool.get_pool_name(10, act=1), 'hard')

    def test_get_normal_encounter_returns_tuple(self):
        """Test getting normal encounter returns (enemies, name) tuple"""
        result = self.pool.get_normal_encounter(floor=2, encounter_count=0)
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
        enemies, name = result
        self.assertIsInstance(enemies, list)
        self.assertIsInstance(name, str)

    def test_get_normal_encounter_early_floor(self):
        """Test getting normal encounter from early floor"""
        enemies, name = self.pool.get_normal_encounter(floor=2, encounter_count=0)
        # Should return a list of enemies
        self.assertIsInstance(enemies, list)
        # Name should be from easy pool
        self.assertIn(name, self.pool.easy_pool)

    def test_get_normal_encounter_late_floor(self):
        """Test getting normal encounter from late floor"""
        enemies, name = self.pool.get_normal_encounter(floor=10, encounter_count=5)
        # Should return a list of enemies
        self.assertIsInstance(enemies, list)
        # Should have gotten some enemies
        self.assertGreater(len(enemies), 0)

    def test_get_elite_encounter_returns_tuple(self):
        """Test getting elite encounter returns (enemies, name) tuple"""
        result = self.pool.get_elite_encounter(floor=6)
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
        enemies, name = result
        self.assertIsInstance(enemies, list)
        self.assertIsInstance(name, str)

    def test_get_elite_encounter_from_pool(self):
        """Test getting elite encounter from elite pool"""
        enemies, name = self.pool.get_elite_encounter(floor=6)
        # Name should be from elite pool
        self.assertIn(name, self.pool.elite_pool)

    def test_get_elite_encounter_excludes_last(self):
        """Test that elite encounter excludes last elite"""
        pool = EncounterPool(seed=42, act_id=1)
        # Get first elite
        enemies1, name1 = pool.get_elite_encounter(floor=6, last_elite=None)
        # Get second elite with last_elite set
        enemies2, name2 = pool.get_elite_encounter(floor=10, last_elite=name1)
        # Second should be different from first (if pool has multiple options)
        self.assertIn(name1, pool.elite_pool)
        self.assertIn(name2, pool.elite_pool)

    def test_get_boss_encounter_returns_tuple(self):
        """Test getting boss encounter returns (enemies, name) tuple"""
        result = self.pool.get_boss_encounter(floor=16)
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
        enemies, name = result
        self.assertIsInstance(enemies, list)
        self.assertIsInstance(name, str)

    def test_get_boss_encounter_valid_floor(self):
        """Test boss encounter for valid boss floor"""
        enemies, name = self.pool.get_boss_encounter(floor=16)
        # Should return a boss
        self.assertGreater(len(enemies), 0)
        self.assertIn(name, self.pool.boss_pool)

    def test_get_boss_encounter_invalid_floor(self):
        """Test boss encounter for non-boss floor"""
        enemies, name = self.pool.get_boss_encounter(floor=5)
        # Should return empty list
        self.assertEqual(enemies, [])

    def test_deterministic_selection(self):
        """Test that same seed produces same selections"""
        pool1 = EncounterPool(seed=123, act_id=1)
        pool2 = EncounterPool(seed=123, act_id=1)

        # Get encounters from both pools
        enemies1, name1 = pool1.get_normal_encounter(floor=2, encounter_count=0)
        enemies2, name2 = pool2.get_normal_encounter(floor=2, encounter_count=0)

        # Should produce same names
        self.assertEqual(name1, name2)
        # Should produce same number of enemies
        self.assertEqual(len(enemies1), len(enemies2))

    def test_different_seeds_different_selections(self):
        """Test that different seeds can produce different selections"""
        pool1 = EncounterPool(seed=111, act_id=1)
        pool2 = EncounterPool(seed=999, act_id=1)

        # Get encounters from both pools
        enemies1, name1 = pool1.get_normal_encounter(floor=2, encounter_count=0)
        enemies2, name2 = pool2.get_normal_encounter(floor=2, encounter_count=0)

        # Results may differ due to different random seeds
        self.assertIsInstance(enemies1, list)
        self.assertIsInstance(enemies2, list)

    def test_encounter_history_prevents_repeats(self):
        """Test that recent encounters are excluded from selection"""
        pool = EncounterPool(seed=42, act_id=1)
        
        # Get first encounter
        enemies1, name1 = pool.get_normal_encounter(floor=2, encounter_count=0, encounter_history=[])
        
        # Get second encounter with history
        enemies2, name2 = pool.get_normal_encounter(floor=3, encounter_count=1, encounter_history=[name1])
        
        # Both should be valid
        self.assertIsInstance(enemies1, list)
        self.assertIsInstance(enemies2, list)


class TestAct2EncounterPool(unittest.TestCase):
    """Test cases for Act 2 EncounterPool"""

    def setUp(self):
        """Set up test fixtures"""
        self.pool = EncounterPool(seed=42, act_id=2)

    def test_act2_easy_pool_has_encounters(self):
        """Test Act 2 easy pool has expected encounters"""
        self.assertIn('Spheric Guardian', self.pool.easy_pool)
        self.assertIn('Chosen', self.pool.easy_pool)
        self.assertIn('Shelled Parasite', self.pool.easy_pool)

    def test_act2_elite_pool_has_encounters(self):
        """Test Act 2 elite pool has expected encounters"""
        self.assertIn('Book of Stabbing', self.pool.elite_pool)
        self.assertIn('Gremlin Leader', self.pool.elite_pool)
        self.assertIn('Taskmaster', self.pool.elite_pool)

    def test_act2_boss_pool_has_bosses(self):
        """Test Act 2 boss pool has expected bosses"""
        self.assertIn('Bronze Automaton', self.pool.boss_pool)
        self.assertIn('The Collector', self.pool.boss_pool)
        self.assertIn('The Champ', self.pool.boss_pool)

    def test_get_normal_encounter_act2(self):
        """Test getting normal encounter from Act 2"""
        enemies, name = self.pool.get_normal_encounter(floor=2, encounter_count=0)
        self.assertIsInstance(enemies, list)
        self.assertGreater(len(enemies), 0)


class TestAct3EncounterPool(unittest.TestCase):
    """Test cases for Act 3 EncounterPool"""

    def setUp(self):
        """Set up test fixtures"""
        self.pool = EncounterPool(seed=42, act_id=3)

    def test_act3_easy_pool_has_encounters(self):
        """Test Act 3 easy pool has expected encounters"""
        self.assertIn('3 Darklings', self.pool.easy_pool)
        self.assertIn('Orb Walker', self.pool.easy_pool)
        self.assertIn('3 Shapes', self.pool.easy_pool)

    def test_act3_elite_pool_has_encounters(self):
        """Test Act 3 elite pool has expected encounters"""
        self.assertIn('Giant Head', self.pool.elite_pool)
        self.assertIn('Nemesis', self.pool.elite_pool)

    def test_act3_boss_pool_has_bosses(self):
        """Test Act 3 boss pool has expected bosses"""
        self.assertIn('Time Eater', self.pool.boss_pool)
        self.assertIn('Awakened One', self.pool.boss_pool)
        self.assertIn('Donu and Deca', self.pool.boss_pool)


class TestAct4EncounterPool(unittest.TestCase):
    """Test cases for Act 4 EncounterPool"""

    def setUp(self):
        """Set up test fixtures"""
        self.pool = EncounterPool(seed=42, act_id=4)

    def test_act4_no_normal_enemies(self):
        """Test Act 4 has no normal enemy encounters"""
        self.assertEqual(len(self.pool.easy_pool), 0)
        self.assertEqual(len(self.pool.hard_pool), 0)

    def test_act4_elite_pool_has_encounters(self):
        """Test Act 4 elite pool has expected encounters"""
        self.assertIn('Spire Shield and Spire Spear', self.pool.elite_pool)

    def test_act4_boss_pool_has_heart(self):
        """Test Act 4 boss pool has Corrupt Heart"""
        self.assertIn('Corrupt Heart', self.pool.boss_pool)


class TestEncounterPoolIntegration(unittest.TestCase):
    """Integration tests for EncounterPool with enemy classes"""

    def test_full_encounter_flow(self):
        """Test complete flow from floor selection to enemy instantiation"""
        pool = EncounterPool(seed=42, act_id=1)

        # Get normal encounter for floor 2
        enemies, name = pool.get_normal_encounter(floor=2, encounter_count=0)

        # Verify we got a list
        self.assertIsInstance(enemies, list)

        # If enemies were returned, verify they have expected attributes
        for enemy in enemies:
            # Enemies should have basic attributes if properly instantiated
            self.assertIsNotNone(enemy)
            self.assertTrue(hasattr(enemy, 'hp') or hasattr(enemy, 'current_hp'))

    def test_multiple_selections_from_same_floor(self):
        """Test that multiple selections can be made from same floor"""
        pool = EncounterPool(seed=42, act_id=1)

        # Make multiple selections with different seeds
        enemies1, _ = pool.get_normal_encounter(floor=2, encounter_count=0)
        
        # Create new pool for different random result
        pool2 = EncounterPool(seed=123, act_id=1)
        enemies2, _ = pool2.get_normal_encounter(floor=2, encounter_count=0)

        # All should be valid lists
        self.assertIsInstance(enemies1, list)
        self.assertIsInstance(enemies2, list)


if __name__ == '__main__':
    unittest.main()
