"""Tests for enemy intention system."""

import unittest
from enemies import JawWorm, Cultist, SpikeSlime, SpikeSlimeM


class TestJawWormIntention(unittest.TestCase):
    """Test JawWorm intention system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.enemy = JawWorm()
    
    def test_intentions_registered(self):
        """Test that all intentions are registered."""
        self.assertIn("chomp", self.enemy.intentions)
        self.assertIn("bellow", self.enemy.intentions)
        self.assertIn("thrash", self.enemy.intentions)
    
    def test_first_turn_act1(self):
        """Test first turn always starts with Chomp in Act 1."""
        intention = self.enemy.determine_next_intention(floor=1)
        self.assertEqual(intention.name, "chomp")
        
        intention = self.enemy.determine_next_intention(floor=10)
        self.assertEqual(intention.name, "chomp")
    
    def test_first_turn_act3(self):
        """Test first turn in Act 3 has random choice."""
        # Test multiple times to check randomness
        results = set()
        for _ in range(50):
            enemy = JawWorm()  # Fresh enemy for each test
            intention = enemy.determine_next_intention(floor=17)
            results.add(intention.name)
        
        # Should see at least one of each possibility in 50 tries
        # But since it's random, we'll just check we get multiple types
        self.assertGreater(len(results), 1)
    
    def test_after_chomp(self):
        """Test intentions after Chomp."""
        # Simulate Chomp
        self.enemy.current_intention = self.enemy.intentions["chomp"]
        self.enemy.history_intentions.append("chomp")
        
        # Next should be mostly Bellow, sometimes Thrash
        bellow_count = 0
        thrash_count = 0
        
        for _ in range(100):
            enemy = JawWorm()
            enemy.history_intentions = ["chomp"]
            intention = enemy.determine_next_intention(floor=1)
            if intention.name == "bellow":
                bellow_count += 1
            else:
                thrash_count += 1
        
        # Bellow should be more common (~59%)
        self.assertGreater(bellow_count, 40)
        self.assertGreater(thrash_count, 20)
    
    def test_execute_intention(self):
        """Test that intention executes and returns actions."""
        from engine.game_state import game_state
        
        # Set up a minimal game state for testing
        self.enemy.current_intention = self.enemy.intentions["chomp"]
        actions = self.enemy.execute_intention()
        
        # Should return a list of actions
        self.assertIsInstance(actions, list)
        
        # History should be updated
        self.assertIn("chomp", self.enemy.history_intentions)


class TestCultistIntention(unittest.TestCase):
    """Test Cultist intention system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.enemy = Cultist()
    
    def test_intentions_registered(self):
        """Test that all intentions are registered."""
        self.assertIn("ritual", self.enemy.intentions)
        self.assertIn("attack", self.enemy.intentions)
    
    def test_first_turn(self):
        """Test first turn always uses Ritual."""
        intention = self.enemy.determine_next_intention(floor=1)
        self.assertEqual(intention.name, "ritual")
    
    def test_after_ritual(self):
        """Test after Ritual always uses Attack."""
        self.enemy.history_intentions.append("ritual")
        intention = self.enemy.determine_next_intention(floor=1)
        self.assertEqual(intention.name, "attack")
    
    def test_after_attack(self):
        """Test after Attack always uses Attack."""
        self.enemy.history_intentions = ["ritual", "attack"]
        intention = self.enemy.determine_next_intention(floor=1)
        self.assertEqual(intention.name, "attack")


class TestSpikeSlimeIntention(unittest.TestCase):
    """Test SpikeSlime intention system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.enemy = SpikeSlime()
    
    def test_intentions_registered(self):
        """Test that all intentions are registered."""
        self.assertIn("lick", self.enemy.intentions)
        self.assertIn("flame_tackle", self.enemy.intentions)
        self.assertIn("split", self.enemy.intentions)
    
    def test_first_turn(self):
        """Test first turn pattern."""
        # First turn should be 30% Flame Tackle, 70% Lick
        lick_count = 0
        flame_tackle_count = 0
        
        for _ in range(100):
            enemy = SpikeSlime()
            intention = enemy.determine_next_intention(floor=1)
            if intention.name == "lick":
                lick_count += 1
            elif intention.name == "flame_tackle":
                flame_tackle_count += 1
        
        # Lick should be more common (~70%)
        self.assertGreater(lick_count, 50)
        self.assertGreater(flame_tackle_count, 10)
    
    def test_split_on_damage(self):
        """Test that split triggers at 50% HP."""
        # Set HP below 50%
        self.enemy.hp = self.enemy.max_hp // 2
        
        # Take damage should trigger split
        modified_damage = self.enemy.on_damage_taken(5)
        
        # Split should be triggered
        self.assertTrue(self.enemy._split_triggered)
        self.assertEqual(self.enemy.current_intention.name, "split")
    
    def test_no_three_same_moves(self):
        """Test that same move cannot be used three times in a row."""
        # Simulate two Licks
        self.enemy.history_intentions = ["lick", "lick"]
        
        # Next should NOT be lick
        intention = self.enemy.determine_next_intention(floor=1)
        self.assertNotEqual(intention.name, "lick")


class TestSpikeSlimeMIntention(unittest.TestCase):
    """Test SpikeSlimeM (medium) intention system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.enemy = SpikeSlimeM()
    
    def test_intentions_registered(self):
        """Test that all intentions are registered."""
        self.assertIn("lick", self.enemy.intentions)
        self.assertIn("flame_tackle", self.enemy.intentions)
    
    def test_no_split_intention(self):
        """Test that medium slime doesn't have split."""
        self.assertNotIn("split", self.enemy.intentions)
    
    def test_first_turn(self):
        """Test first turn pattern."""
        # First turn should be 30% Flame Tackle, 70% Lick
        lick_count = 0
        flame_tackle_count = 0
        
        for _ in range(100):
            enemy = SpikeSlimeM()
            intention = enemy.determine_next_intention(floor=1)
            if intention.name == "lick":
                lick_count += 1
            elif intention.name == "flame_tackle":
                flame_tackle_count += 1
        
        # Lick should be more common (~70%)
        self.assertGreater(lick_count, 50)
        self.assertGreater(flame_tackle_count, 10)


if __name__ == '__main__':
    unittest.main()