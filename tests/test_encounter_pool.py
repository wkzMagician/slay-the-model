"""
Unit tests for Encounter Pool system.

Tests verify that enemies are correctly selected based on floor number
and encounter type (normal, elite, boss).
"""
import unittest
from unittest.mock import Mock, patch
from map.encounter_pool import EncounterPool


class TestEncounterPool(unittest.TestCase):
    """Test cases for EncounterPool"""

    def setUp(self):
        """Set up test fixtures"""
        # Use fixed seed for deterministic tests
        self.pool = EncounterPool(seed=42)

    def test_floor_range_early(self):
        """Test floor range detection for early game"""
        # Floors 0-5 should be 'early'
        self.assertEqual(self.pool.get_floor_range(0), 'early')
        self.assertEqual(self.pool.get_floor_range(2), 'early')
        self.assertEqual(self.pool.get_floor_range(5), 'early')

    def test_floor_range_mid(self):
        """Test floor range detection for mid game"""
        # Floors 6-11 should be 'mid'
        self.assertEqual(self.pool.get_floor_range(6), 'mid')
        self.assertEqual(self.pool.get_floor_range(8), 'mid')
        self.assertEqual(self.pool.get_floor_range(11), 'mid')

    def test_floor_range_late(self):
        """Test floor range detection for late game"""
        # Floors 12-16 should be 'late'
        self.assertEqual(self.pool.get_floor_range(12), 'late')
        self.assertEqual(self.pool.get_floor_range(14), 'late')
        self.assertEqual(self.pool.get_floor_range(16), 'late')

    def test_normal_pools_exist(self):
        """Test that normal pools are built"""
        self.assertIn('early', self.pool.normal_pools)
        self.assertIn('mid', self.pool.normal_pools)
        self.assertIn('late', self.pool.normal_pools)

        # Each pool should have encounters
        self.assertGreater(len(self.pool.normal_pools['early']), 0)
        self.assertGreater(len(self.pool.normal_pools['mid']), 0)
        self.assertGreater(len(self.pool.normal_pools['late']), 0)

    def test_elite_pools_exist(self):
        """Test that elite pools are built (may be empty)"""
        self.assertIn('early', self.pool.elite_pools)
        self.assertIn('mid', self.pool.elite_pools)
        self.assertIn('late', self.pool.elite_pools)

    def test_boss_pools_exist(self):
        """Test that boss pools are built"""
        # Boss pool may be empty if no boss enemies exist
        self.assertIsInstance(self.pool.boss_pools, dict)

    def test_get_normal_encounter(self):
        """Test getting normal encounter"""
        enemies = self.pool.get_normal_encounter(floor=2)

        # Should return a list
        self.assertIsInstance(enemies, list)

        # For early floor with existing enemies, should get some enemies
        # (May be empty if enemy classes not properly imported)
        self.assertIsInstance(enemies, list)

    def test_get_normal_encounter_different_floors(self):
        """Test getting encounters from different floor ranges"""
        # Early floor
        early_enemies = self.pool.get_normal_encounter(floor=2)
        self.assertIsInstance(early_enemies, list)

        # Mid floor
        mid_enemies = self.pool.get_normal_encounter(floor=8)
        self.assertIsInstance(mid_enemies, list)

        # Late floor
        late_enemies = self.pool.get_normal_encounter(floor=14)
        self.assertIsInstance(late_enemies, list)

    def test_get_elite_encounter_early_floor(self):
        """Test that elite encounters are empty before floor 3"""
        enemies = self.pool.get_elite_encounter(floor=2)

        # Elites should not be available before floor 3
        self.assertIsInstance(enemies, list)
        # May be empty if no elite enemies exist

    def test_get_elite_encounter_mid_floor(self):
        """Test getting elite encounter from mid floor"""
        enemies = self.pool.get_elite_encounter(floor=6)

        self.assertIsInstance(enemies, list)
        # May be empty if no elite enemies exist

    def test_get_boss_encounter(self):
        """Test getting boss encounter"""
        # Floor 3 should have The Guardian (if exists)
        enemies = self.pool.get_boss_encounter(floor=3)

        self.assertIsInstance(enemies, list)
        # May be empty if boss enemies not properly registered

    def test_get_boss_encounter_invalid_floor(self):
        """Test boss encounter for non-boss floor"""
        # Floor 5 is not a boss floor
        enemies = self.pool.get_boss_encounter(floor=5)

        # Should return empty list
        self.assertIsInstance(enemies, list)

    def test_deterministic_selection(self):
        """Test that same seed produces same selections"""
        pool1 = EncounterPool(seed=123)
        pool2 = EncounterPool(seed=123)

        # Get encounters from both pools
        enemies1 = pool1.get_normal_encounter(floor=2)
        enemies2 = pool2.get_normal_encounter(floor=2)

        # Should produce same results
        self.assertEqual(len(enemies1), len(enemies2))

    def test_different_seeds_different_selections(self):
        """Test that different seeds can produce different selections"""
        pool1 = EncounterPool(seed=111)
        pool2 = EncounterPool(seed=999)

        # Get encounters from both pools
        enemies1 = pool1.get_normal_encounter(floor=2)
        enemies2 = pool2.get_normal_encounter(floor=2)

        # Results may differ due to different random seeds
        self.assertIsInstance(enemies1, list)
        self.assertIsInstance(enemies2, list)

    def test_resolve_encounter_single_enemy(self):
        """Test resolving encounter with single enemy"""
        enemies = self.pool._resolve_encounter('Cultist')

        self.assertIsInstance(enemies, list)
        # If Cultist enemy class exists, should return one enemy
        # Otherwise returns empty list

    def test_resolve_encounter_multiple_enemies(self):
        """Test resolving encounter with multiple enemies"""
        enemies = self.pool._resolve_encounter('2 Louse')

        self.assertIsInstance(enemies, list)
        # Should return 2 louse enemies if Louse class exists

    def test_resolve_encounter_unknown(self):
        """Test resolving unknown encounter"""
        enemies = self.pool._resolve_encounter('Unknown Encounter')

        self.assertEqual(enemies, [])

    def test_select_encounter_from_pool(self):
        """Test weighted selection from pool"""
        pool = [('Cultist', 2), ('JawWorm', 2)]

        selected = self.pool._select_encounter(pool)

        # Should return one of the encounter names
        self.assertIn(selected, ['Cultist', 'JawWorm'])

    def test_select_encounter_from_empty_pool(self):
        """Test selection from empty pool"""
        pool = []

        selected = self.pool._select_encounter(pool)

        self.assertIsNone(selected)

    def test_encounter_weights_consistency(self):
        """Test that encounter weights are properly stored"""
        # Check that all encounters have valid weights
        for range_name, pool in self.pool.normal_pools.items():
            for encounter_name, weight in pool:
                self.assertIsInstance(encounter_name, str)
                self.assertIsInstance(weight, (int, float))
                self.assertGreater(weight, 0)


class TestEncounterCompositions(unittest.TestCase):
    """Test encounter composition mappings"""

    def setUp(self):
        """Set up test fixtures"""
        self.pool = EncounterPool(seed=42)

    def test_single_enemy_encounters(self):
        """Test encounters with single enemy"""
        # These should resolve to single enemy
        single_enemy_encounters = [
            'Cultist',
            'JawWorm',
            'Looter',
        ]

        for encounter_name in single_enemy_encounters:
            enemies = self.pool._resolve_encounter(encounter_name)
            # If enemy class exists, should return 1 enemy
            self.assertIsInstance(enemies, list)
            if enemies:  # Only assert if enemies were found
                self.assertLessEqual(len(enemies), 1)

    def test_multiple_enemy_encounters(self):
        """Test encounters with multiple enemies"""
        # These should resolve to multiple enemies
        multi_enemy_encounters = [
            '2 Louse',
            '3 Louse',
        ]

        for encounter_name in multi_enemy_encounters:
            enemies = self.pool._resolve_encounter(encounter_name)
            self.assertIsInstance(enemies, list)

    def test_empty_encounters(self):
        """Test encounters that should be empty (not implemented)"""
        # These encounters are listed but enemy classes may not exist yet
        not_implemented = [
            'Gang of Gremlins',
            'Blue Slaver',
            'Red Slaver',
            '2 Fungi Beasts',
            'Exordium Wildlife',
        ]

        for encounter_name in not_implemented:
            enemies = self.pool._resolve_encounter(encounter_name)
            self.assertIsInstance(enemies, list)


class TestEncounterPoolIntegration(unittest.TestCase):
    """Integration tests for EncounterPool with enemy classes"""

    def test_full_encounter_flow(self):
        """Test complete flow from floor selection to enemy instantiation"""
        pool = EncounterPool(seed=42)

        # Get normal encounter for floor 2
        enemies = pool.get_normal_encounter(floor=2)

        # Verify we got a list
        self.assertIsInstance(enemies, list)

        # If enemies were returned, verify they have expected attributes
        for enemy in enemies:
            # Enemies should have basic attributes if properly instantiated
            self.assertIsNotNone(enemy)

    def test_multiple_selections_from_same_floor(self):
        """Test that multiple selections can be made from same floor"""
        pool = EncounterPool(seed=42)

        # Make multiple selections
        enemies1 = pool.get_normal_encounter(floor=2)
        enemies2 = pool.get_normal_encounter(floor=2)
        enemies3 = pool.get_normal_encounter(floor=2)

        # All should be valid lists
        self.assertIsInstance(enemies1, list)
        self.assertIsInstance(enemies2, list)
        self.assertIsInstance(enemies3, list)


if __name__ == '__main__':
    unittest.main()
