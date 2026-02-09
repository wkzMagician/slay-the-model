from typing import TYPE_CHECKING, List

from entities import Creature
from player.card_manager import CardManager
from player.orb_manager import OrbManager
from player.status_manager import StatusManager
from entities.collection import Collection
from utils.types import StatusType

if TYPE_CHECKING:
    from actions.base import Action


class Player(Creature):
    character: str = "Player"
    base_max_hp = 70
    base_energy = 3
    starting_gold = 99
    starting_deck = []
    orb_slots = 1
    base_potion_limit = 3

    def __init__(self):
        from cards.namespaces import get_namespace_for_character
        self.namespace = get_namespace_for_character(self.character)

        # Initialize Creature base class
        super().__init__(max_hp=self.__class__.base_max_hp)

        # Initialize managers
        self.card_manager = CardManager(self.__class__.starting_deck)
        self.orb_manager = OrbManager(getattr(self.__class__, "orb_slots", 1))
        self.status_manager = StatusManager(StatusType.NEUTRAL)

        # Stats
        self._gold = self.__class__.starting_gold
        self.potions = Collection(self.__class__.base_potion_limit)
        self.relics = Collection()

        # Combat-related properties
        self.max_energy = self.__class__.base_energy
        self._energy = self.__class__.base_energy

        # Draw count (base, can be modified by relics/powers)
        self.base_draw_count = 5

    @property
    def draw_count(self) -> int:
        """Get current draw count (base + modifiers)."""
        return self.base_draw_count

        # Draw count (base, can be modified by relics/powers)
        self.base_draw_count = 5

    def on_death(self) -> List['Action']:
        """Handle player death by setting game over phase."""
        from actions import GameOverAction
        return [GameOverAction()]

    @property
    def gold(self) -> int:
        return self._gold

    @gold.setter
    def gold(self, value: int) -> None:
        self._gold = max(0, int(value))

    @property
    def energy(self) -> int:
        return self._energy

    @energy.setter
    def energy(self, value: int) -> None:
        self._energy = max(0, min(int(value), self.max_energy))

    @property
    def potion_limit(self) -> int:
        return self.potions.limit

    @potion_limit.setter
    def potion_limit(self, value: int) -> None:
        self.potions.trim_to_limit(value)

    def gain_energy(self, amount=1):
        if amount <= 0:
            return self.energy
        self.energy += amount
        return self.energy