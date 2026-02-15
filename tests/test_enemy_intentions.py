"""Tests for enemy intention system."""

import unittest
from enemies import (
    JawWorm, Cultist, SpikeSlime, SpikeSlimeM,
    FungiBeast, RedLouse, GreenLouse, BlueSlaver, RedSlaver,
    TheGuardian, SlimeBoss, TheHexaghost
)


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


class TestFungiBeastIntention(unittest.TestCase):
    """Test FungiBeast intention system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.enemy = FungiBeast()
    
    def test_intentions_registered(self):
        """Test that all intentions are registered."""
        self.assertIn("bite", self.enemy.intentions)
        self.assertIn("grow", self.enemy.intentions)
    
    def test_first_turn(self):
        """Test first turn has valid intention."""
        intention = self.enemy.determine_next_intention(floor=1)
        self.assertIn(intention.name, ["bite", "grow"])
    
    def test_no_three_bites_in_row(self):
        """Test that Bite cannot be used 3 times in a row."""
        self.enemy.history_intentions = ["bite", "bite"]
        intention = self.enemy.determine_next_intention(floor=1)
        self.assertEqual(intention.name, "grow")
    
    def test_no_two_grows_in_row(self):
        """Test that Grow cannot be used 2 times in a row."""
        self.enemy.history_intentions = ["grow"]
        intention = self.enemy.determine_next_intention(floor=1)
        self.assertEqual(intention.name, "bite")
    
    def test_hp_range(self):
        """Test HP is in expected range."""
        self.assertGreaterEqual(self.enemy.max_hp, 22)
        self.assertLessEqual(self.enemy.max_hp, 28)


class TestRedLouseIntention(unittest.TestCase):
    """Test RedLouse intention system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.enemy = RedLouse()
    
    def test_intentions_registered(self):
        """Test that all intentions are registered."""
        self.assertIn("bite", self.enemy.intentions)
        self.assertIn("grow", self.enemy.intentions)
    
    def test_first_turn(self):
        """Test first turn has valid intention."""
        intention = self.enemy.determine_next_intention(floor=1)
        self.assertIn(intention.name, ["bite", "grow"])
    
    def test_no_three_same_moves(self):
        """Test that same move cannot be used 3 times in a row."""
        # Test bite
        self.enemy.history_intentions = ["bite", "bite"]
        intention = self.enemy.determine_next_intention(floor=1)
        self.assertEqual(intention.name, "grow")
        
        # Test grow
        self.enemy.history_intentions = ["grow", "grow"]
        intention = self.enemy.determine_next_intention(floor=1)
        self.assertEqual(intention.name, "bite")
    
    def test_curl_up_attribute(self):
        """Test Curl Up attribute exists."""
        self.assertTrue(hasattr(self.enemy, '_curl_up'))
        self.assertGreaterEqual(self.enemy._curl_up, 3)
        self.assertLessEqual(self.enemy._curl_up, 7)


class TestGreenLouseIntention(unittest.TestCase):
    """Test GreenLouse intention system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.enemy = GreenLouse()
    
    def test_intentions_registered(self):
        """Test that all intentions are registered."""
        self.assertIn("bite", self.enemy.intentions)
        self.assertIn("spit_web", self.enemy.intentions)
    
    def test_first_turn(self):
        """Test first turn has valid intention."""
        intention = self.enemy.determine_next_intention(floor=1)
        self.assertIn(intention.name, ["bite", "spit_web"])
    
    def test_no_three_same_moves(self):
        """Test that same move cannot be used 3 times in a row."""
        # Test bite
        self.enemy.history_intentions = ["bite", "bite"]
        intention = self.enemy.determine_next_intention(floor=1)
        self.assertEqual(intention.name, "spit_web")
        
        # Test spit_web
        self.enemy.history_intentions = ["spit_web", "spit_web"]
        intention = self.enemy.determine_next_intention(floor=1)
        self.assertEqual(intention.name, "bite")


class TestBlueSlaverIntention(unittest.TestCase):
    """Test BlueSlaver intention system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.enemy = BlueSlaver()
    
    def test_intentions_registered(self):
        """Test that all intentions are registered."""
        self.assertIn("stab", self.enemy.intentions)
        self.assertIn("rake", self.enemy.intentions)
    
    def test_first_turn(self):
        """Test first turn has valid intention."""
        intention = self.enemy.determine_next_intention(floor=1)
        self.assertIn(intention.name, ["stab", "rake"])
    
    def test_no_three_same_moves(self):
        """Test that same move cannot be used 3 times in a row."""
        self.enemy.history_intentions = ["stab", "stab"]
        intention = self.enemy.determine_next_intention(floor=1)
        self.assertEqual(intention.name, "rake")


class TestRedSlaverIntention(unittest.TestCase):
    """Test RedSlaver intention system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.enemy = RedSlaver()
    
    def test_intentions_registered(self):
        """Test that all intentions are registered."""
        self.assertIn("stab", self.enemy.intentions)
        self.assertIn("scrape", self.enemy.intentions)
        self.assertIn("entangle", self.enemy.intentions)
    
    def test_first_turn(self):
        """Test first turn is always Stab."""
        intention = self.enemy.determine_next_intention(floor=1)
        self.assertEqual(intention.name, "stab")
    
    def test_entangle_once_only(self):
        """Test that Entangle can only be used once."""
        # Force entangle use
        self.enemy._entangle_used = True
        # Run many turns
        for _ in range(50):
            intention = self.enemy.determine_next_intention(floor=1)
            self.enemy.history_intentions.append(intention.name)
        
        # Entangle should never appear after being used
        self.assertNotIn("entangle", self.enemy.history_intentions)


class TestTheGuardianIntention(unittest.TestCase):
    """Test TheGuardian (Boss) intention system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.enemy = TheGuardian()
    
    def test_intentions_registered(self):
        """Test that all intentions are registered."""
        self.assertIn("charging_up", self.enemy.intentions)
        self.assertIn("fierce_bash", self.enemy.intentions)
        self.assertIn("vent_steam", self.enemy.intentions)
        self.assertIn("whirlwind", self.enemy.intentions)
        self.assertIn("defensive_mode", self.enemy.intentions)
        self.assertIn("roll_attack", self.enemy.intentions)
        self.assertIn("twin_slam", self.enemy.intentions)
    
    def test_first_turn(self):
        """Test first turn is Charging Up."""
        intention = self.enemy.determine_next_intention(floor=1)
        self.assertEqual(intention.name, "charging_up")
    
    def test_main_pattern(self):
        """Test main attack pattern."""
        expected = ["charging_up", "fierce_bash", "vent_steam", "whirlwind"]
        for i, exp in enumerate(expected):
            intention = self.enemy.determine_next_intention(floor=1)
            self.assertEqual(intention.name, exp, f"Turn {i+1} should be {exp}")
    
    def test_fixed_hp(self):
        """Test boss has fixed HP."""
        self.assertEqual(self.enemy.max_hp, 240)
    
    def test_boss_flag(self):
        """Test boss flag is set."""
        from utils.types import EnemyType
        self.assertEqual(self.enemy.enemy_type, EnemyType.BOSS)


class TestSlimeBossIntention(unittest.TestCase):
    """Test SlimeBoss intention system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.enemy = SlimeBoss()
    
    def test_intentions_registered(self):
        """Test that all intentions are registered."""
        self.assertIn("goop_spray", self.enemy.intentions)
        self.assertIn("preparing", self.enemy.intentions)
        self.assertIn("slam", self.enemy.intentions)
        self.assertIn("split", self.enemy.intentions)
    
    def test_first_turn(self):
        """Test first turn is Goop Spray."""
        intention = self.enemy.determine_next_intention(floor=1)
        self.assertEqual(intention.name, "goop_spray")
    
    def test_pattern(self):
        """Test attack pattern."""
        expected = ["goop_spray", "preparing", "slam"]
        for i, exp in enumerate(expected):
            intention = self.enemy.determine_next_intention(floor=1)
            self.assertEqual(intention.name, exp, f"Turn {i+1} should be {exp}")
    
    def test_fixed_hp(self):
        """Test boss has fixed HP."""
        self.assertEqual(self.enemy.max_hp, 140)
    
    def test_boss_flag(self):
        """Test boss flag is set."""
        from utils.types import EnemyType
        self.assertEqual(self.enemy.enemy_type, EnemyType.BOSS)


class TestTheHexaghostIntention(unittest.TestCase):
    """Test TheHexaghost (Final Boss) intention system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.enemy = TheHexaghost()
    
    def test_intentions_registered(self):
        """Test that all intentions are registered."""
        self.assertIn("activate", self.enemy.intentions)
        self.assertIn("divider", self.enemy.intentions)
        self.assertIn("sear", self.enemy.intentions)
        self.assertIn("tackle", self.enemy.intentions)
        self.assertIn("inflame", self.enemy.intentions)
        self.assertIn("inferno", self.enemy.intentions)
    
    def test_first_turn(self):
        """Test first turn is Activate."""
        intention = self.enemy.determine_next_intention(floor=1)
        self.assertEqual(intention.name, "activate")
    
    def test_second_turn(self):
        """Test second turn is Divider."""
        self.enemy.determine_next_intention(floor=1)  # Turn 1: Activate
        intention = self.enemy.determine_next_intention(floor=1)  # Turn 2
        self.assertEqual(intention.name, "divider")
    
    def test_main_pattern(self):
        """Test main attack pattern after first two turns."""
        # Skip first two turns
        self.enemy.determine_next_intention(floor=1)
        self.enemy.determine_next_intention(floor=1)
        
        expected = ["sear", "tackle", "sear", "inflame", "tackle", "sear", "inferno"]
        for exp in expected:
            intention = self.enemy.determine_next_intention(floor=1)
            self.assertEqual(intention.name, exp)
    
    def test_fixed_hp(self):
        """Test boss has fixed HP."""
        self.assertEqual(self.enemy.max_hp, 250)
    
    def test_boss_flag(self):
        """Test boss flag is set."""
        from utils.types import EnemyType
        self.assertEqual(self.enemy.enemy_type, EnemyType.BOSS)


if __name__ == '__main__':
    unittest.main()