"""Orb management for the player."""

from typing import List, Optional, TypeVar, Union

Orb = TypeVar('Orb')
OrbType = str


class OrbManager:
    """Manages orbs for the player."""

    def __init__(self, max_orb_slots: int = 1) -> None:
        self._orbs: List[Union[Orb, OrbType]] = []
        self._max_orb_slots = max_orb_slots

    @property
    def orbs(self) -> List[Union[Orb, OrbType]]:
        return self._orbs

    @property
    def max_orb_slots(self) -> int:
        return self._max_orb_slots

    @max_orb_slots.setter
    def max_orb_slots(self, value: int) -> None:
        self._max_orb_slots = max(0, int(value))
        # If new max slots is less than current orb count, evoke excess orbs
        while len(self._orbs) > self._max_orb_slots:
            self.evoke_orb()

    def add_orb(self, orb: Union[Orb, OrbType]) -> None:
        """Add an orb. If max slots exceeded, evoke rightmost orb first."""
        if len(self._orbs) >= self._max_orb_slots:
            self.evoke_orb()
        self._orbs.append(orb)

    def evoke_orb(self, index: Optional[int] = None) -> Optional[Union[Orb, OrbType]]:
        """Evoke an orb (remove and return it). Defaults to rightmost orb."""
        if not self._orbs:
            return None
        if index is None:
            index = len(self._orbs) - 1
        if index < 0 or index >= len(self._orbs):
            return None
        return self._orbs.pop(index)

    def remove_orb(self, index: int) -> Optional[Union[Orb, OrbType]]:
        """Remove an orb at specific index without evoking."""
        if not self._orbs or index < 0 or index >= len(self._orbs):
            return None
        return self._orbs.pop(index)

    def clear_all(self) -> None:
        """Remove all orbs without evoking."""
        self._orbs.clear()

    def get_orb_count(self) -> int:
        """Get current number of orbs."""
        return len(self._orbs)

    def has_orb_type(self, orb_type: OrbType) -> bool:
        """Check if player has a specific type of orb."""
        for orb in self._orbs:
            if getattr(orb, "orb_type", str(orb)) == orb_type:
                return True
        return False

    def get_orb_by_type(self, orb_type: OrbType) -> Optional[Union[Orb, OrbType]]:
        """Get first orb of specific type."""
        for orb in self._orbs:
            if getattr(orb, "orb_type", str(orb)) == orb_type:
                return orb
        return None

    def trigger_passives(self, timing: str) -> None:
        """Trigger orb passives based on timing."""
        for orb in list(self._orbs):
            if getattr(orb, "passive_timing", None) == timing:
                orb.trigger_passive()

    def record_orb_generation(self, orb_type, amount=1):
        """Track how many of each orb type have been channeled."""
        from engine.game_state import game_state
        if not orb_type or amount <= 0:
            return
        game_state.combat_state.record_orb_generation(orb_type, amount)

    def get_orb_generation_count(self, orb_type):
        """How many of a given orb type were channeled this combat."""
        from engine.game_state import game_state
        return game_state.combat_state.get_orb_generation_count(orb_type)

    def channel_orb(self, orb_type, amount=1):
        if not orb_type or amount <= 0:
            return
        from game.localization import t
        from game.orbs import create_orb

        for _ in range(amount):
            orb = create_orb(orb_type)
            if not orb:
                continue
            self.add_orb(orb)
            orb_key = getattr(orb, "orb_type", None) or getattr(orb, "name", None)
            self.record_orb_generation(orb_key)
            print(t(
                "combat.channel_orb",
                default=f"Channel {orb.name}.",
                orb=orb.name,
            ))

    def evoke_orb_with_effect(self, index=None, target=None):
        orb = self.evoke_orb(index)
        if orb:
            orb.evoke(target)
            from game.localization import t
            print(t(
                "combat.evoke_orb",
                default=f"Evoke {orb.name}.",
                orb=orb.name,
            ))
        return orb
