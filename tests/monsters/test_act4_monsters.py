"""Test Act 4 monsters - Spire Shield, Spire Spear, Corrupt Heart"""
from engine.random_streams import get_rng, StreamRandom
import unittest
from unittest.mock import patch

from enemies.act4.spire_shield import SpireShield
from enemies.act4.spire_spear import SpireSpear
from enemies.act4.corrupt_heart import CorruptHeart
from enemies.act4.spire_shield_intentions import Bash, Fortify, Smash
from enemies.act4.spire_spear_intentions import BurnStrike, Piercer, Skewer
from enemies.act4.corrupt_heart_intentions import (
    BeatOfDeathPower,
    BloodShots,
    BuffHeart,
    Debilitate,
    Echo,
)
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
        self.assertIn("Smash", shield.intentions)
    
    def test_intention_types(self):
        """Test intention types are correct"""
        shield = SpireShield()
        self.assertIsInstance(shield.intentions["Bash"], Bash)
        self.assertIsInstance(shield.intentions["Fortify"], Fortify)
        self.assertIsInstance(shield.intentions["Smash"], Smash)
    
    def test_pattern_starts_with_bash(self):
        """Test Spire Shield starts with Bash"""
        with patch.object(
            StreamRandom, "choice",
            return_value=["Bash", "Fortify"],
        ):
            shield = SpireShield()
            intention = shield.determine_next_intention(1)
            self.assertEqual(intention, "Bash")
    
    def test_pattern_sequence(self):
        """Test Spire Shield turn pattern with Smash every 3 turns."""
        with patch.object(
            StreamRandom, "choice",
            side_effect=[
                ["Bash", "Fortify"],
                ["Fortify", "Bash"],
            ],
        ):
            shield = SpireShield()
            self.assertEqual(shield.determine_next_intention(1), "Bash")
            self.assertEqual(shield.determine_next_intention(2), "Fortify")
            self.assertEqual(shield.determine_next_intention(3), "Smash")
            self.assertEqual(shield.determine_next_intention(4), "Fortify")
            self.assertEqual(shield.determine_next_intention(5), "Bash")
            self.assertEqual(shield.determine_next_intention(6), "Smash")


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
        self.assertIn("Burn Strike", spear.intentions)
        self.assertIn("Skewer", spear.intentions)
        self.assertIn("Piercer", spear.intentions)
    
    def test_intention_types(self):
        """Test intention types are correct"""
        spear = SpireSpear()
        self.assertIsInstance(spear.intentions["Burn Strike"], BurnStrike)
        self.assertIsInstance(spear.intentions["Skewer"], Skewer)
        self.assertIsInstance(spear.intentions["Piercer"], Piercer)
    
    def test_pattern_starts_with_burn_strike(self):
        """Test Spire Spear starts with Burn Strike"""
        spear = SpireSpear()
        intention = spear.determine_next_intention(1)
        self.assertEqual(intention, "Burn Strike")
    
    def test_pattern_sequence(self):
        """Test Spear turn pattern with Skewer every 3 turns from turn 2."""
        with patch.object(
            StreamRandom, "choice",
            return_value=["Burn Strike", "Piercer"],
        ):
            spear = SpireSpear()
            self.assertEqual(spear.determine_next_intention(1), "Burn Strike")
            self.assertEqual(spear.determine_next_intention(2), "Skewer")
            self.assertEqual(spear.determine_next_intention(3), "Burn Strike")
            self.assertEqual(spear.determine_next_intention(4), "Piercer")
            self.assertEqual(spear.determine_next_intention(5), "Skewer")


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
        self.assertIn("Blood Shots", heart.intentions)
        self.assertIn("Echo", heart.intentions)
        self.assertIn("Buff", heart.intentions)
    
    def test_starts_with_beat_of_death_power(self):
        """Test Corrupt Heart starts combat with Beat of Death."""
        heart = CorruptHeart()
        self.helper.start_combat([heart])
        power_names = [power.name for power in heart.powers]
        self.assertIn("Beat of Death", power_names)
    
    def test_pattern_rules(self):
        """Test Corrupt Heart uses Debilitate first and Buff every 3 turns."""
        with patch.object(
            StreamRandom, "choice",
            side_effect=[
                ["Blood Shots", "Echo"],
                ["Echo", "Blood Shots"],
            ],
        ):
            heart = CorruptHeart()
            self.assertEqual(heart.determine_next_intention(1), "Debilitate")
            self.assertEqual(heart.determine_next_intention(2), "Blood Shots")
            self.assertEqual(heart.determine_next_intention(3), "Echo")
            self.assertEqual(heart.determine_next_intention(4), "Buff")
            self.assertEqual(heart.determine_next_intention(5), "Echo")
            self.assertEqual(heart.determine_next_intention(6), "Blood Shots")
            self.assertEqual(heart.determine_next_intention(7), "Buff")
    
    def test_debilitate_actions(self):
        """Test Debilitate applies 3 debuffs and adds 5 status cards."""
        from engine.game_state import game_state
        heart = CorruptHeart()
        game_state.action_queue.clear()
        heart.intentions["Debilitate"].execute()
        self.assertEqual(len(game_state.action_queue.queue), 8)

    def test_buff_intention_type(self):
        """Test Buff intention class remains correct."""
        heart = CorruptHeart()
        self.assertIsInstance(heart.intentions["Buff"], BuffHeart)
    
    def test_bloodshots_and_echo_intention_types(self):
        """Test Heart attack intentions are correctly registered."""
        heart = CorruptHeart()
        self.assertIsInstance(heart.intentions["Blood Shots"], BloodShots)
        self.assertIsInstance(heart.intentions["Echo"], Echo)

    def test_beat_of_death_power_class(self):
        """Test BeatOfDeathPower class is available."""
        heart = CorruptHeart()
        power = BeatOfDeathPower(amount=1, owner=heart)
        self.assertEqual(power.name, "Beat of Death")


if __name__ == '__main__':
    unittest.main()
