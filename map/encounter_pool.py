"""Encounter pool system for selecting enemies based on floor.

This system manages:
- Normal encounters (common enemies)
- Elite encounters (elite enemies)
- Boss encounters (boss enemies)
Encounters are selected based on floor number and enemy availability.

Pool structure based on enemies/enemy_pool.md:
- Act 1 Easy Pool: First 3 encounters
- Act 1 Hard Pool: Remaining encounters
- Boss floors: 3, 8, 16
"""

from typing import List, Dict, Tuple, Optional
import random

# Import enemy classes (avoid circular imports at module level)
_ENEMY_CLASSES = None


def _get_enemy_classes():
    """Lazy import of enemy classes to avoid circular dependencies."""
    global _ENEMY_CLASSES
    if _ENEMY_CLASSES is None:
        from enemies import __all__ as enemy_names
        from enemies import __dict__ as enemy_module

        _ENEMY_CLASSES = {
            name: enemy_module[name]
            for name in enemy_names
            if name in enemy_module and name != 'Enemy'
        }
    return _ENEMY_CLASSES


class EncounterPool:
    """
    Manages enemy encounter pools for different room types.

    Pools are organized by:
    - Enemy type (normal, elite, boss)
    - Floor ranges (early, mid, late game)
    - Encounter combinations with weights
    """

    # Floor ranges for encounter selection
    FLOOR_RANGES = {
        'early': (0, 6),      # Floors 0-5
        'mid': (6, 12),        # Floors 6-11
        'late': (12, 17)       # Floors 12-16
    }

    def __init__(self, seed: int):
        """
        Initialize encounter pool.

        Args:
            seed: Random seed for deterministic selection
        """
        self.seed = seed
        self.rng = random.Random(seed)

        # Build encounter pools
        self.normal_pools = self._build_normal_pools()
        self.elite_pools = self._build_elite_pools()
        self.boss_pools = self._build_boss_pools()

    def _build_normal_pools(self) -> Dict[str, List[Tuple[str, int]]]:
        """
        Build normal encounter pools by floor range.

        Returns:
            Dict mapping floor range to list of (enemy_name, weight) tuples
        """
        enemy_classes = _get_enemy_classes()

        # Act 1 Easy Pool: First 3 encounters (floors 0-2)
        # Cultist (weight 2): 1 cultist
        # Jaw Worm (weight 2): 1 jaw worm
        # 2 Louse (weight 2): 2 lice (each independently 50% red or green)
        # Small Slimes (weight 2): Spiked Slime (M) + Acid Slime (S) or Spiked Slime (M) + Acid Slime (S)
        easy_encounters = [
            ('Cultist', 2),
            ('JawWorm', 2),
            ('2 Louse', 2),
            ('Small Slimes', 2),
        ]

        # Act 1 Hard Pool: Remaining encounters (floors 3+)
        # Gang of Gremlins (weight 1): 4 from 2x Fat, 2x Sneaky, 2x Mad, Shield, Wizard
        # Large Slime (weight 2): Spiked Slime (L) or Acid Slime (L)
        # Swarm of Slimes (weight 1): 3x Spiked Slime (S) + 2x Acid Slime (S)
        # Blue Slaver (weight 1): 1 blue slaver
        # Red Slaver (weight 1): 1 red slaver
        # 3 Louse (weight 2): 3 lice (each independently 50% red or green)
        # 2 Fungi Beasts (weight 2): 2 fungi beasts
        # Exordium Thugs (weight 1.5): First enemy: Louse or Medium Slime; Second: Slaver, Cultist, or Looter
        # Exordium Wildlife (weight 1.5): First enemy: Fungi Beast or Jaw Worm; Second: Louse or Medium Slime
        # Looter (weight 2): 1 looter

        hard_encounters = [
            ('Gang of Gremlins', 1),
            ('Large Slime', 2),
            ('Swarm of Slimes', 1),
            ('Blue Slaver', 1),
            ('Red Slaver', 1),
            ('3 Louse', 2),
            ('2 Fungi Beasts', 2),
            ('Exordium Thugs', 1.5),
            ('Exordium Wildlife', 1.5),
            ('Looter', 2),
        ]

        # For now: use same pools for all floor ranges
        # In full implementation, early/mid/late would have different pools
        return {
            'early': easy_encounters + hard_encounters,
            'mid': easy_encounters + hard_encounters,
            'late': easy_encounters + hard_encounters,
        }

    def _build_elite_pools(self) -> Dict[str, List[Tuple[str, int]]]:
        """
        Build elite encounter pools by floor range.

        Returns:
            Dict mapping floor range to list of (enemy_name, weight) tuples
        """
        # No elite enemies exist yet, return empty pools
        return {
            'early': [],
            'mid': [],
            'late': [],
        }

    def _build_boss_pools(self) -> Dict[int, Tuple[str, Dict[str, str]]]:
        """
        Build boss encounter pool by boss floor.

        Returns:
            Dict mapping floor number to (boss_name, {details})
        """
        enemy_classes = _get_enemy_classes()

        # Check for existing boss enemy files
        boss_pools = {}

        # Map bosses based on enemy_pool.md
        # Floor 3: TheGuardian
        # Floor 8: SlimeBoss
        # Floor 16: TheHexaghost (final boss)

        # Look for boss enemies by name pattern
        for name, cls in enemy_classes.items():
            if hasattr(cls, 'enemy_type') and cls.enemy_type.value == 'Boss':
                if 'TheGuardian' in name or 'Guardian' in name:
                    boss_pools[3] = (name, {
                        'floor': 3,
                        'name': 'The Guardian',
                    })
                elif 'SlimeBoss' in name or ('Slime' in name and 'Boss' in name):
                    boss_pools[8] = (name, {
                        'floor': 8,
                        'name': 'Slime Boss',
                    })
                elif 'TheHexaghost' in name or 'Hexaghost' in name:
                    boss_pools[16] = (name, {
                        'floor': 16,
                        'name': 'The Hexaghost',
                    })

        return boss_pools

    def get_floor_range(self, floor: int) -> str:
        """
        Get floor range category for given floor.

        Args:
            floor: Floor number

        Returns:
            'early', 'mid', or 'late'
        """
        for range_name, (min_floor, max_floor) in self.FLOOR_RANGES.items():
            if min_floor <= floor < max_floor:
                return range_name
        return 'late'  # Fallback

    def _select_encounter(self, pool: List[Tuple[str, int]]) -> Optional[str]:
        """
        Select a random encounter from the weighted pool.

        Args:
            pool: List of (encounter_name, weight) tuples

        Returns:
            The selected encounter name, or None if pool is empty
        """
        if not pool:
            return None

        # Extract names and weights
        names = [item[0] for item in pool]
        weights = [item[1] for item in pool]

        # Weighted random selection
        return self.rng.choices(names, weights=weights, k=1)[0]

    def get_normal_encounter(self, floor: int) -> List:
        """
        Get normal enemies for given floor.

        Args:
            floor: Current floor number

        Returns:
            List of instantiated enemy objects
        """
        enemy_classes = _get_enemy_classes()
        range_name = self.get_floor_range(floor)
        pool = self.normal_pools.get(range_name, [])

        if not pool:
            return []

        # Select encounter from weighted pool
        encounter_name = self._select_encounter(pool)
        if not encounter_name:
            return []

        # Resolve encounter combination to actual enemies
        enemies = self._resolve_encounter(encounter_name)

        return enemies

    def get_elite_encounter(self, floor: int) -> List:
        """
        Get elite enemy for given floor.

        Args:
            floor: Current floor number

        Returns:
            List with single elite enemy object
        """
        # Elites only available from floor 3+
        if floor < 3:
            return []

        enemy_classes = _get_enemy_classes()
        range_name = self.get_floor_range(floor)
        pool = self.elite_pools.get(range_name, [])

        if not pool:
            return []

        # Select and instantiate elite enemy
        selected_name = self._select_encounter(pool)
        if not selected_name:
            return []

        # Resolve encounter to actual enemies
        enemies = self._resolve_encounter(selected_name)

        return enemies

    def get_boss_encounter(self, floor: int) -> List:
        """
        Get boss enemy for given floor.

        Args:
            floor: Boss floor number

        Returns:
            List with single boss enemy object
        """
        if floor not in self.boss_pools:
            return []

        enemy_classes = _get_enemy_classes()
        boss_name, details = self.boss_pools[floor]

        if not boss_name or boss_name not in enemy_classes:
            return []

        # Instantiate boss
        boss = enemy_classes[boss_name]()
        return [boss]

    def _resolve_encounter(self, encounter_name: str) -> List:
        """
        Resolve encounter name to actual enemy instances.

        Args:
            encounter_name: Name of encounter from pool

        Returns:
            List of instantiated enemy objects
        """
        enemy_classes = _get_enemy_classes()

        # Map encounter names to actual enemy compositions
        encounter_compositions = {
            'Cultist': ['Cultist'],
            'JawWorm': ['JawWorm'],
            '2 Louse': ['Louse', 'Louse'],  # 2 lice
            'Small Slimes': ['SpikeSlime', 'SpikeSlimeM'],  # Spiked Slime (M) + Acid Slime (S)
            'Gang of Gremlins': [],  # Need to implement gremlins
            'Large Slime': ['SpikeSlime'],  # Spiked Slime (L) or Acid Slime (L)
            'Swarm of Slimes': ['SpikeSlime', 'SpikeSlime', 'SpikeSlimeM'],  # 3x Spiked Slime (S) + 2x Acid Slime (S)
            'Blue Slaver': [],  # Need to implement slavers
            'Red Slaver': [],  # Need to implement slavers
            '3 Louse': ['Louse', 'Louse', 'Louse'],  # 3 lice
            '2 Fungi Beasts': [],  # Need to implement fungi beasts
            'Exordium Thugs': ['Louse', 'Looter'],  # First: Louse; Second: Looter
            'Exordium Wildlife': [],  # First: Fungi Beast or Jaw Worm; Second: Louse or Medium Slime
            'Looter': ['Looter'],  # Need to implement looter
        }

        enemy_names = encounter_compositions.get(encounter_name, [])
        if not enemy_names:
            return []

        # Instantiate enemies
        enemies = []
        for name in enemy_names:
            if name in enemy_classes:
                enemy = enemy_classes[name]()
                enemies.append(enemy)

        return enemies
