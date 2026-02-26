"""Test intention field fix"""
# -*- coding: utf-8 -*-
import sys
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'
sys.path.insert(0, '.')

from enemies.act1.acid_slime_intentions import LickIntention
from enemies.act1.spike_slime_intentions import LickIntention as SpikeLickIntention


class MockEnemy:
    """Mock enemy object"""
    def __init__(self, class_name):
        self.__class__.__name__ = class_name


def test_acid_slime_lick():
    """Test Acid Slime LickIntention"""
    # Test AcidSlimeL (should have 2 weak)
    enemy = MockEnemy('AcidSlimeL')
    intention = LickIntention(enemy)
    
    # Check field name
    assert hasattr(intention, 'weak_stacks'), "Should have weak_stacks attribute"
    assert intention.weak_stacks == 2, f"AcidSlimeL should have 2 weak, got {intention.weak_stacks}"
    
    print("[OK] Acid Slime L - weak_stacks correctly set to 2")
    
    # Test AcidSlimeM/S (should have 1 weak)
    enemy = MockEnemy('AcidSlimeM')
    intention = LickIntention(enemy)
    assert hasattr(intention, 'weak_stacks'), "Should have weak_stacks attribute"
    assert intention.weak_stacks == 1, f"AcidSlimeM should have 1 weak, got {intention.weak_stacks}"
    
    print("[OK] Acid Slime M/S - weak_stacks correctly set to 1")


def test_spike_slime_lick():
    """Test Spike Slime LickIntention"""
    enemy = MockEnemy('SpikeSlimeS')
    intention = SpikeLickIntention(enemy)
    
    # Spike Slime uses base_amount for frail stacks
    assert hasattr(intention, 'base_amount'), "Should have base_amount attribute"
    assert intention.base_amount == 2, f"SpikeSlime should have 2 frail, got {intention.base_amount}"
    
    print("[OK] Spike Slime - base_amount correctly set to 2")


if __name__ == '__main__':
    print("Testing Intention field fix...\n")
    
    test_acid_slime_lick()
    print()
    test_spike_slime_lick()
    
    print("\nAll tests passed!")