"""Test orb action system refactor."""

import unittest
from orbs.dark import DarkOrb
from actions.orb import (
    OrbPassiveAction,
    OrbEvokeAction,
    TriggerOrbPassivesAction,
    EvokeOrbAction,
    EvokeAllOrbsAction,
    AddOrbAction,
)
from utils.result_types import MultipleActionsResult, NoneResult


class TestDarkOrb(unittest.TestCase):
    """Test DarkOrb with new Action API."""

    def setUp(self):
        self.orb = DarkOrb()

    def test_on_passive_increases_charge(self):
        """Test that on_passive increases charge."""
        initial_charge = self.orb.charge
        result = self.orb.on_passive()
        
        # on_passive should return None (no actions needed)
        self.assertIsNone(result)
        
        # Charge should increase
        self.assertGreater(self.orb.charge, initial_charge)

    def test_on_evoke_returns_actions(self):
        """Test that on_evoke returns list of actions."""
        actions = self.orb.on_evoke()
        
        # Should return a list of actions
        self.assertIsNotNone(actions)
        self.assertIsInstance(actions, list)
        self.assertGreater(len(actions), 0)

    def test_on_evoke_action_has_deal_damage(self):
        """Test that on_evoke returns DealDamageAction."""
        from actions.combat import DealDamageAction
        
        actions = self.orb.on_evoke()
        
        # Should contain a DealDamageAction
        self.assertTrue(any(isinstance(action, DealDamageAction) for action in actions))


class TestOrbPassiveAction(unittest.TestCase):
    """Test OrbPassiveAction."""

    def test_execute_returns_multiple_actions(self):
        """Test that OrbPassiveAction executes correctly."""
        orb = DarkOrb()
        action = OrbPassiveAction(orb=orb)
        
        result = action.execute()
        
        # DarkOrb.on_passive returns None, so result should be NoneResult
        self.assertIsInstance(result, NoneResult)


class TestOrbEvokeAction(unittest.TestCase):
    """Test OrbEvokeAction."""

    def test_execute_returns_multiple_actions(self):
        """Test that OrbEvokeAction executes correctly."""
        orb = DarkOrb()
        action = OrbEvokeAction(orb=orb)
        
        result = action.execute()
        
        # Should return MultipleActionsResult with DealDamageAction
        self.assertIsInstance(result, MultipleActionsResult)
        self.assertGreater(len(result.actions), 0)


class TestOrbAPICompatibility(unittest.TestCase):
    """Test that old API methods still exist but are deprecated."""

    def test_orb_base_has_on_passive(self):
        """Test that Orb base class has on_passive method."""
        from orbs.base import Orb
        
        self.assertTrue(hasattr(Orb, 'on_passive'))
        self.assertTrue(callable(Orb.on_passive))

    def test_orb_base_has_on_evoke(self):
        """Test that Orb base class has on_evoke method."""
        from orbs.base import Orb
        
        self.assertTrue(hasattr(Orb, 'on_evoke'))
        self.assertTrue(callable(Orb.on_evoke))

    def test_dark_orb_implements_new_methods(self):
        """Test that DarkOrb implements new methods."""
        orb = DarkOrb()
        
        self.assertTrue(hasattr(orb, 'on_passive'))
        self.assertTrue(hasattr(orb, 'on_evoke'))
        self.assertTrue(callable(orb.on_passive))
        self.assertTrue(callable(orb.on_evoke))


if __name__ == '__main__':
    unittest.main()