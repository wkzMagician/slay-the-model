"""Tests for Shelled Parasite Plated Armor and stun mechanics."""
import unittest
from unittest.mock import Mock

from enemies.act2.shelled_parasite import ShelledParasite
from engine.message_bus import MessageBus
from engine.messages import AnyHpLostMessage


class TestShelledParasitePlatedArmor(unittest.TestCase):
    """Test Plated Armor initialization and stun mechanics."""
    
    def test_starts_with_plated_armor_14(self):
        """Shelled Parasite should start with 14 Plated Armor."""
        enemy = ShelledParasite()
        enemy.on_combat_start()
        
        plated_armor = None
        for power in enemy.powers:
            if power.name == "Plated Armor":
                plated_armor = power
                break
        
        self.assertIsNotNone(plated_armor)
        assert plated_armor is not None
        self.assertEqual(plated_armor.amount, 14)
    
    def test_plated_armor_decreases_on_attack_damage(self):
        """Plated Armor should decrease when taking attack damage."""
        enemy = ShelledParasite()
        enemy.on_combat_start()
        
        plated_armor = None
        for power in enemy.powers:
            if power.name == "Plated Armor":
                plated_armor = power
                break
        
        self.assertIsNotNone(plated_armor)
        assert plated_armor is not None
        initial_amount = plated_armor.amount
        
        # Simulate attack damage on power
        plated_armor.on_physical_attack_taken(5)
        
        self.assertEqual(plated_armor.amount, initial_amount - 1)
    
    def test_plated_armor_not_decrease_on_non_attack(self):
        """Plated Armor should NOT decrease on non-attack damage."""
        enemy = ShelledParasite()
        enemy.on_combat_start()
        
        plated_armor = None
        for power in enemy.powers:
            if power.name == "Plated Armor":
                plated_armor = power
                break
        
        self.assertIsNotNone(plated_armor)
        assert plated_armor is not None
        initial_amount = plated_armor.amount
        
        # Simulate non-attack damage (e.g., poison, card effect)
        # Non-physical damage should not consume plated armor stacks.
        MessageBus().publish(
            AnyHpLostMessage(target=enemy, amount=5, source=Mock(), card=None),
            participants=[enemy],
        )
        
        self.assertEqual(plated_armor.amount, initial_amount)
    
    def test_stunned_when_plated_armor_reaches_zero(self):
        """Shelled Parasite should enter Stunned when Plated Armor reaches 0."""
        enemy = ShelledParasite()
        enemy.on_combat_start()
        
        # Reduce Plated Armor to 1 (so next damage will trigger 0)
        plated_armor = None
        for power in enemy.powers:
            if power.name == "Plated Armor":
                plated_armor = power
                break
        
        self.assertIsNotNone(plated_armor)
        assert plated_armor is not None
        plated_armor.amount = 1
        
        # Simulate damage that triggers the reduction to 0 (must be attack type)
        enemy.on_physical_attack_taken(5, source=Mock())
        
        # Find power again (may have been updated)
        plated_armor = None
        for power in enemy.powers:
            if power.name == "Plated Armor":
                plated_armor = power
                break
        
        # Either power is gone or amount is 0
        if plated_armor:
            self.assertEqual(plated_armor.amount, 0)
        
        # Should be stunned
        self.assertEqual(enemy.current_intention.name, "stunned")
        self.assertTrue(enemy._has_been_stunned)
    
    def test_stun_only_happens_once(self):
        """Stun should only happen once per combat."""
        enemy = ShelledParasite()
        enemy.on_combat_start()
        
        # Set Plated Armor to 0
        plated_armor = None
        for power in enemy.powers:
            if power.name == "Plated Armor":
                plated_armor = power
                break
        
        if plated_armor:
            plated_armor.amount = 0
        
        # Trigger first stun
        enemy.on_physical_attack_taken(5)
        self.assertTrue(enemy._has_been_stunned)
        
        # Reset intention manually
        enemy.current_intention = enemy.intentions["double_strike"]
        
        # Try to trigger again - should not change
        enemy.on_physical_attack_taken(5)
        # Should still be double_strike (not forced back to stunned)
        self.assertEqual(enemy.current_intention.name, "double_strike")
    
    def test_no_stun_before_plated_armor_zero(self):
        """Shelled Parasite should NOT stun while Plated Armor > 0."""
        enemy = ShelledParasite()
        enemy.on_combat_start()
        
        # Take damage while Plated Armor is still high
        enemy.on_physical_attack_taken(5)
        
        # Should NOT be stunned
        self.assertFalse(enemy._has_been_stunned)
        # current_intention might not be set yet (depends on combat flow)
        # but it definitely shouldn't be "stunned"
        if hasattr(enemy, 'current_intention') and enemy.current_intention:
            self.assertNotEqual(enemy.current_intention.name, "stunned")


if __name__ == "__main__":
    unittest.main()
