from entities import Creature
from player.card_manager import CardManager
from player.orb_manager import OrbManager
from player.status_manager import StatusManager
from player.potion_collection import PotionCollection


class Player(Creature):
    character: str = "Player"
    base_max_hp = 70
    base_energy = 3
    starting_gold = 99
    starting_deck = []
    orb_slots = 1
    base_potion_limit = 3

    def __init__(self):
        from game.cards.namespaces import get_namespace_for_character
        self.namespace = get_namespace_for_character(self.character)

        # Initialize Creature base class
        super().__init__(max_hp=self.__class__.base_max_hp)
        
        # Initialize managers
        self.card_manager = CardManager(self.__class__.starting_deck)
        self.orb_manager = OrbManager(getattr(self.__class__, "orb_slots", 1))
        self.status_manager = StatusManager("Calm")

        # Stats
        self._gold = self.__class__.starting_gold
        self.relics = []
        self._potion_limit = self.__class__.base_potion_limit
        self._potions = PotionCollection(self, [])

        # Combat-related properties
        self.max_energy = self.__class__.base_energy
        self._energy = self.__class__.base_energy

        self.set_on_death(self._handle_death)

    def _handle_death(self, _creature=None):
        try:
            from engine.game_state import game_state
            if hasattr(game_state, "handle_creature_death"):
                game_state.handle_creature_death(self)
            elif getattr(game_state, "combat_state", None):
                game_state.combat_state.game_phase = "game_over"
        except Exception:
            pass

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
        return self._potion_limit

    @potion_limit.setter
    def potion_limit(self, value: int) -> None:
        self._potion_limit = max(0, int(value))
        if len(self._potions) > self._potion_limit:
            self._potions.trim_to_limit()

    @property
    def potions(self):
        return self._potions

    def gain_energy(self, amount=1):
        if amount <= 0:
            return self.energy
        self.energy += amount
        return self.energy
