"""Base creature entity shared by player and enemies."""

from typing import List, Optional, Callable, Any

from localization import Localizable


class Creature(Localizable):
    """Base creature with health, block, and powers.

    The on_death callback allows the game manager to respond to death events.
    """

    def __init__(
        self,
        max_hp: int,
        powers: Optional[List[Any]] = None,
        on_death: Optional[Callable[["Creature"], None]] = None,
    ) -> None:
        self._max_hp = max_hp
        self._hp = max_hp
        self._block = 0
        self.powers: List[Any] = list(powers or [])
        self._on_death = on_death

    @property
    def max_hp(self) -> int:
        return self._max_hp

    @max_hp.setter
    def max_hp(self, value: int) -> None:
        self._hp += value - self._max_hp
        self._max_hp = max(1, int(value))

    @property
    def block(self) -> int:
        return self._block

    @block.setter
    def block(self, value: int) -> None:
        self._block = max(0, int(value))

    def set_on_death(self, callback: Optional[Callable[["Creature"], None]]) -> None:
        self._on_death = callback

    def is_dead(self) -> bool:
        return self._hp <= 0

    @property
    def hp(self) -> int:
        return self._hp

    @hp.setter
    def hp(self, value: int) -> None:
        self._hp = max(0, min(self.max_hp, int(value)))
        if self.is_dead():
            self.on_death()

    def take_damage(self, amount: int, source=None, card=None, damage_type: str = "direct") -> int:
        if amount <= 0:
            return 0
        damage = amount
        for power in list(self.powers):
            if hasattr(power, "on_damage_taken"):
                damage = power.on_damage_taken(
                    damage,
                    source=source,
                    card=card,
                    player=self,
                    damage_type=damage_type,
                )
        if damage <= 0:
            return 0

        absorbed = min(self.block, damage)
        self.block -= absorbed
        remaining = damage - absorbed
        if remaining > 0:
            self.hp -= remaining
        return remaining

    def heal(self, amount: int) -> int:
        if amount <= 0:
            return 0
        self.hp += amount
        return self._hp

    def gain_block(self, amount: int, source=None, card=None) -> None:
        if amount <= 0:
            return None
        self.block += amount
        for power in list(self.powers):
            if hasattr(power, "on_gain_block"):
                actions = power.on_gain_block(amount, player=self, source=source, card=card)
                if actions and isinstance(actions, list):
                    from engine.game_state import game_state
                    game_state.action_queue.add_actions(actions)

    def add_power(self, power) -> None:
        if not power:
            return
        for existing in self.powers:
            if existing.name == power.name and existing.stackable:
                if getattr(power, "amount", 0):
                    existing.amount += power.amount
                if getattr(power, "duration", 0):
                    existing.duration += power.duration
                return
        power.owner = self
        self.powers.append(power)

    def remove_power(self, power_name: str) -> None:
        self.powers = [p for p in self.powers if p.name != power_name]

    def get_power(self, power_name: str):
        if not power_name:
            return None
        lookup = str(power_name).lower()
        for power in list(self.powers):
            if getattr(power, "name", "").lower() == lookup:
                return power
        return None

    def on_death(self) -> None:
        if self._on_death:
            self._on_death(self)