"""Test Act 4 monsters - Spire Shield, Spire Spear, Corrupt Heart"""
import unittest
from enemies.act4.spire_shield import SpireShield
from enemies.act4.spire_spear import SpireSpear
from enemies.act4.corrupt_heart import CorruptHeart
from enemies.act4.spire_shield_intentions import Bash, Fortify, Smite
from enemies.act4.spire_spear_intentions import Skewer, SearingBurn, Pierce
from enemies.act4.corrupt_heart_intentions import Debilitate, AttackHeart, BloodShots, Echo, BuffHeart
from tests.test_combat_utils import CombatTestHelper
from utils.types import EnemyType


class TestSpireShield(unittest.TestCase):
    """Test Spire Shield Elite enemy"""
    
    def setUp(self):
        self.helper = CombatTestHelper()
    
    def tearDown(self):
        self.helper._reset_game_state()
    
    def test_hp_range(self):
        """Test Spire Shield has correct HP range (42-48)"""
        shield = SpireShield()
        self.assertGreaterEqual(shield.hp, 42)
        self.assertLessEqual(shield.hp, 48)
    
    def test_is_elite(self):
        """Test Spire Shield is Elite type"""
        shield = SpireShield()
        self.assertEqual(shield.enemy_type, EnemyType.ELITE)
    
    def test_has_intentions(self):
        """Test Spire Shield has all intentions"""
        shield = SpireShield()
        self.assertIn("Bash", shield.intentions)
        self.assertIn("Fortify", shield.intentions)
        self.assertIn("Smite", shield.intentions)
    
    def test_intention_types(self):
        """Test intention types are correct"""
        shield = SpireShield()
        self.assertIsInstance(shield.intentions["Bash"], Bash)
        self.assertIsInstance(shield.intentions["Fortify"], Fortify)
        self.assertIsInstance(shield.intentions["Smite"], Smite)
    
    def test_pattern_starts_with_bash(self):
        """Test Spire Shield starts with Bash"""
        shield = SpireShield()
        intention = shield.determine_next_intention(1)
        self.assertEqual(intention, "Bash")
    
    def test_pattern_sequence(self):
        """Test Spire Shield follows pattern: Bash -> Fortify -> Smite"""
        shield = SpireShield()
        self.assertEqual(shield.determine_next_intention(1), "Bash")
        self.assertEqual(shield.determine_next_intention(2), "Fortify")
        self.assertEqual(shield.determine_next_intention(3), "Smite")
        self.assertEqual(shield.determine_next_intention(4), "Bash")


class TestSpireSpear(unittest.TestCase):
    """Test Spire Spear Elite enemy"""
    
    def setUp(self):
        self.helper = CombatTestHelper()
    
    def tearDown(self):
        self.helper._reset_game_state()
    
    def test_hp_range(self):
        """Test Spire Spear has correct HP range (38-42)"""
        spear = SpireSpear()
        self.assertGreaterEqual(spear.hp, 38)
        self.assertLessEqual(spear.hp, 42)
    
    def test_is_elite(self):
        """Test Spire Spear is Elite type"""
        spear = SpireSpear()
        self.assertEqual(spear.enemy_type, EnemyType.ELITE)
    
    def test_has_intentions(self):
        """Test Spire Spear has all intentions"""
        spear = SpireSpear()
        self.assertIn("Skewer", spear.intentions)
        self.assertIn("Searing Burn", spear.intentions)
        self.assertIn("Pierce", spear.intentions)
    
    def test_intention_types(self):
        """Test intention types are correct"""
        spear = SpireSpear()
        self.assertIsInstance(spear.intentions["Skewer"], Skewer)
        self.assertIsInstance(spear.intentions["Searing Burn"], SearingBurn)
        self.assertIsInstance(spear.intentions["Pierce"], Pierce)
    
    def test_pattern_starts_with_skewer(self):
        """Test Spire Spear starts with Skewer"""
        spear = SpireSpear()
        intention = spear.determine_next_intention(1)
        self.assertEqual(intention, "Skewer")
    
    def test_pattern_sequence(self):
        """Test Spire Spear follows pattern: Skewer -> Searing Burn -> Pierce"""
        spear = SpireSpear()
        self.assertEqual(spear.determine_next_intention(1), "Skewer")
        self.assertEqual(spear.determine_next_intention(2), "Searing Burn")
        self.assertEqual(spear.determine_next_intention(3), "Pierce")
        self.assertEqual(spear.determine_next_intention(4), "Skewer")


class TestCorruptHeart(unittest.TestCase):
    """Test Corrupt Heart Final Boss"""
    
    def setUp(self):
        self.helper = CombatTestHelper()
    
    def tearDown(self):
        self.helper._reset_game_state()
    
    def test_hp_range(self):
        """Test Corrupt Heart has correct HP range (750-800)"""
        heart = CorruptHeart()
        self.assertGreaterEqual(heart.hp, 750)
        self.assertLessEqual(heart.hp, 800)
    
    def test_is_boss(self):
        """Test Corrupt Heart is Boss type"""
        heart = CorruptHeart()
        self.assertEqual(heart.enemy_type, EnemyType.BOSS)
    
    def test_has_all_intentions(self):
        """Test Corrupt Heart has all intentions"""
        heart = CorruptHeart()
        self.assertIn("Debilitate", heart.intentions)
        self.assertIn("Invoke", heart.intentions)
        self.assertIn("Attack", heart.intentions)
        self.assertIn("Blood Shots", heart.intentions)
        self.assertIn("Echo", heart.intentions)
        self.assertIn("Buff", heart.intentions)
    
    def test_starts_in_phase_1(self):
        """Test Corrupt Heart starts in Phase 1"""
        heart = CorruptHeart()
        self.assertEqual(heart._phase, 1)
    
    def test_phase_1_pattern(self):
        """Test Phase 1 pattern: Debilitate -> Invoke -> Attack"""
        heart = CorruptHeart()
        self.assertEqual(heart.determine_next_intention(1), "Debilitate")
        self.assertEqual(heart.determine_next_intention(2), "Invoke")
        self.assertEqual(heart.determine_next_intention(3), "Attack")
        self.assertEqual(heart.determine_next_intention(4), "Debilitate")
    
    def test_invincible_hp_tracking(self):
        """Test Corrupt Heart has invincibility mechanic"""
        heart = CorruptHeart()
        self.assertEqual(heart.invincible_hp, 500)
    
    def test_cards_played_tracking(self):
        """Test Corrupt Heart tracks cards played"""
        heart = CorruptHeart()
        self.assertEqual(heart._cards_played, 0)
        self.assertEqual(heart.unique_cards_played, 0)


if __name__ == '__main__':
    unittest.main()
