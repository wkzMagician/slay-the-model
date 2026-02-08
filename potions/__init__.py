# Potions module - Imports all potion definitions
# This file imports all potion classes to register them with the registry system

# Import base potion class
from potions.base import Potion

# Import potion definitions by category
import potions.global_potions
import potions.ironclad
import potions.silent
import potions.defect
import potions.watcher

__all__ = ['Potion']