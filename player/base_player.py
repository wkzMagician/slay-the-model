from entities import Creature
from player.card_manager import CardManager


class Player(Creature):
    character: str = "Player"
    max_health = 70
    base_energy = 3
    starting_gold = 99
    starting_deck = []
    orb_slots = 1
    def __init__(self):
        from game.cards.namespaces import get_namespace_for_character
        self.namespace = get_namespace_for_character(self.character)

        # stats
        super().__init__(max_hp=self.__class__.max_health)
        self.gold = self.__class__.starting_gold

        self.card_manager = CardManager(self._build_starting_deck(self.__class__.starting_deck))
        self.relics = []
        self.potions = []

        self.floor = 1

        # combat
        self.max_energy = self.__class__.base_energy
        self.energy = self.__class__.base_energy

        self.max_orb_slots = getattr(self.__class__, "orb_slots", 1)
        self.orbs = []
        self.status = "Calm" #

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
    def deck(self):
        return self.card_manager.deck

    @property
    def draw_pile(self):
        return self.card_manager.draw_pile

    @property
    def discard_pile(self):
        return self.card_manager.discard_pile

    @property
    def hand(self):
        return self.card_manager.hand

    @property
    def exhaust_pile(self):
        return self.card_manager.exhaust_pile

    @property
    def health(self):
        return self.hp

    @health.setter
    def health(self, value):
        self.hp = value

    @property
    def max_health(self):
        return self.max_hp

    @max_health.setter
    def max_health(self, value):
        self.max_hp = value

    def _set_power_amount(self, power_name, amount, allow_zero=False):
        if power_name is None:
            return None
        try:
            amount = int(amount)
        except Exception:
            amount = 0
        existing = self.get_power(power_name)
        if amount == 0 and not allow_zero:
            if existing:
                self.remove_power(power_name)
            return 0
        if existing:
            existing.amount = amount
            return existing.amount
        from game.powers.registry import create_power
        power = create_power(power_name, amount=amount)
        self.add_power(power)
        return amount

    def _build_starting_deck(self, cards):
        deck = []
        for card_name in cards:
            if "." in card_name:
                deck.append(card_name)
            else:
                prefix = self.namespace or ""
                deck.append(f"{prefix}.{card_name}" if prefix else card_name)
        return deck

    def gain_energy(self, amount=1):
        if amount <= 0:
            return self.energy
        self.energy += amount
        return self.energy

    def gain_orb_slots(self, amount=1):
        """Increase the player's maximum orb slots."""
        try:
            inc = int(amount or 0)
        except Exception:
            inc = 0
        if inc <= 0:
            return self.max_orb_slots
        self.max_orb_slots += inc
        from game.localization import t
        print(t(
            "combat.gain_orb_slots",
            default=f"Gain {inc} Orb slot(s) (total {self.max_orb_slots}).",
            amount=inc,
            total=self.max_orb_slots,
        ))
        return self.max_orb_slots

    def lose_orb_slots(self, amount=1):
        """Reduce the player's maximum orb slots, evoking extras if necessary."""
        try:
            dec = int(amount or 0)
        except Exception:
            dec = 0
        if dec <= 0:
            return self.max_orb_slots
        previous_slots = self.max_orb_slots
        new_total = max(0, previous_slots - dec)
        actual_lost = previous_slots - new_total
        if actual_lost <= 0:
            return self.max_orb_slots
        self.max_orb_slots = new_total
        while len(self.orbs) > self.max_orb_slots:
            self.evoke_orb()
        from game.localization import t
        print(t(
            "combat.lose_orb_slots",
            default=f"Lose {actual_lost} Orb slot(s) (total {self.max_orb_slots}).",
            amount=actual_lost,
            total=self.max_orb_slots,
        ))
        return self.max_orb_slots

    def add_power(self, power):
        if not power:
            return
        for existing in self.powers:
            if existing.name == power.name and existing.stackable:
                if getattr(power, "amount", 0):
                    existing.amount += power.amount
                if getattr(power, "duration", 0):
                    existing.duration += power.duration
                if getattr(existing, "duration_equals_amount", False):
                    existing.amount = existing.duration
                return
        power.owner = self
        self.powers.append(power)
        if getattr(power, "name", "") == "Echo Form":
            self.enable_echo_form_for_next_card()

    def remove_power(self, power_name):
        self.powers = [p for p in self.powers if p.name != power_name]

    def on_turn_start(self):
        for power in list(self.powers):
            power.on_turn_start(self)

    def on_turn_end(self):
        for power in list(self.powers):
            power.on_turn_end(self)

    def gain_block(self, amount, source=None, card=None):
        return super().gain_block(amount, source=source, card=card)

    def apply_pending_block(self):
        """Grant any pending block scheduled for the start of this turn."""
        from engine.game_state import game_state
        pending = game_state.combat_state.pending_block
        if pending <= 0:
            return 0
        game_state.combat_state.pending_block = 0
        self.gain_block(pending, source="pending_block")
        return pending

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
            if len(self.orbs) >= self.max_orb_slots:
                self.evoke_orb()
            self.orbs.append(orb)
            orb_key = getattr(orb, "orb_type", None) or getattr(orb, "name", None)
            self.record_orb_generation(orb_key)
            print(t(
                "combat.channel_orb",
                default=f"Channel {orb.name}.",
                orb=orb.name,
            ))

    def evoke_orb(self, index=None):
        if not self.orbs:
            return None
        if index is None:
            index = len(self.orbs) - 1  # Default to rightmost orb
        if index < 0 or index >= len(self.orbs):
            return None
        orb = self.orbs.pop(index)
        orb.evoke(self)
        from game.localization import t
        print(t(
            "combat.evoke_orb",
            default=f"Evoke {orb.name}.",
            orb=orb.name,
        ))
        return orb

    def trigger_orb_passives(self, timing):
        if not self.orbs:
            return
        for orb in list(self.orbs):
            if getattr(orb, "passive_timing", None) == timing:
                orb.trigger_passive(self)
