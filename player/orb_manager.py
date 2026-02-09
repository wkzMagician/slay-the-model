"""Orb management for the player."""

from typing import List, Optional
from orbs.base import Orb
from actions.base import Action

class OrbManager:
    """Manages orbs for the player."""

    def __init__(self, max_orb_slots: int = 1) -> None:
        self._orbs: List[Orb] = []
        self._max_orb_slots = max_orb_slots

    @property
    def orbs(self) -> List[Orb]:
        return self._orbs

    @property
    def max_orb_slots(self) -> int:
        return self._max_orb_slots

    @max_orb_slots.setter
    def max_orb_slots(self, value: int) -> None:
        value = max(0, int(value))
        if value < self._max_orb_slots:
            self._orbs = self._orbs[:value]
        self._max_orb_slots = value

    def add_orb(self, orb: Orb) -> List[Action]:
        """Add an orb. If max slots exceeded, evoke rightmost orb first.
        
        Args:
            orb: Orb instance to add
            
        Returns:
            List[Action]: List of actions to execute (evoke actions if slot full)
        """
        actions: List[Action] = []
        
        if self._max_orb_slots <= 0:
            return actions
            
        if len(self._orbs) >= self._max_orb_slots:
            # Evoke rightmost orb first
            evoke_actions = self.evoke_orb(index=-1)
            actions.extend(evoke_actions)
            
        self._orbs.append(orb)
        return actions

    def evoke_orb(self, index: int = 0, times: int = 1) -> List[Action]:
        """Evoke an orb from slot, calling its on_evoke method.

        Args:
            index (int): Orb index to evoke (defaults to 0, leftmost). Use -1 for rightmost.
            times (int): Number of times to evoke (default 1)

        Returns:
            List[Action]: List of actions from the orb's on_evoke method
        """
        actions: List[Action] = []
        
        if not self._orbs:
            return actions
            
        # Handle negative index (rightmost)
        if index < 0:
            index = len(self._orbs) + index
            
        if index < 0 or index >= len(self._orbs):
            return actions
            
        orb = self._orbs.pop(index)
        
        # Call orb's on_evoke method multiple times if specified
        for _ in range(times):
            try:
                orb_actions = orb.on_evoke()
                if orb_actions:
                    if isinstance(orb_actions, list):
                        actions.extend(orb_actions)
                    else:
                        actions.append(orb_actions)
            except NotImplementedError:
                pass
                
        return actions

    def remove_orb(self, index: int = 0) -> Optional[Orb]:
        """Remove an orb at specific index without evoking. Defaults to rightmost orb.
        
        Args:
            index (int): Orb index to remove. Use -1 for rightmost.
            
        Returns:
            Optional[Orb]: The removed orb, or None if invalid index
        """
        if not self._orbs:
            return None
            
        # Handle negative index (rightmost)
        if index < 0:
            index = len(self._orbs) + index
            
        if index < 0 or index >= len(self._orbs):
            return None
            
        return self._orbs.pop(index)

    def clear_all(self) -> None:
        """Remove all orbs without evoking."""
        self._orbs.clear()
        
    def evoke_all(self) -> List[Action]:
        """Evoke all orbs from slots, calling their on_evoke methods.

        Returns:
            List[Action]: List of actions from all orbs' on_evoke methods
        """
        actions: List[Action] = []
        
        if not self._orbs:
            return actions
            
        # Get all orbs before clearing
        orbs_to_evoke = list(self._orbs)
        self._orbs.clear()
        
        # Evoke each orb
        for orb in orbs_to_evoke:
            try:
                orb_actions = orb.on_evoke()
                if orb_actions:
                    if isinstance(orb_actions, list):
                        actions.extend(orb_actions)
                    else:
                        actions.append(orb_actions)
            except NotImplementedError:
                pass
                
        return actions

    def get_orb_count(self) -> int:
        """Get current number of orbs."""
        return len(self._orbs)

    def trigger_passives(self, timing: str) -> List[Action]:
        """Trigger passives for all orbs with matching timing.

        Args:
            timing (str): Timing to trigger ("turn_start", "turn_end", etc.)

        Returns:
            List[Action]: List of actions from orbs' on_passive methods
        """
        actions: List[Action] = []
        
        for orb in self._orbs:
            if getattr(orb, "passive_timing", None) == timing:
                try:
                    orb_actions = orb.on_passive()
                    if orb_actions:
                        if isinstance(orb_actions, list):
                            actions.extend(orb_actions)
                        else:
                            actions.append(orb_actions)
                except NotImplementedError:
                    pass
                    
        return actions