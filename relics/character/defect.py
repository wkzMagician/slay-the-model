"""Defect-specific relics."""

from actions.combat import ApplyPowerAction
from actions.orb import AddOrbAction, IncreaseOrbSlotsAction, OrbPassiveAction
from engine.runtime_api import add_action, add_actions
from orbs.dark import DarkOrb
from orbs.frost import FrostOrb
from orbs.lightning import LightningOrb
from orbs.plasma import PlasmaOrb
from powers.definitions.focus import FocusPower
from relics.base import Relic
from utils.registry import register
from utils.types import RarityType


def _trigger_all_orb_passives(player) -> None:
    for orb in list(player.orb_manager.orbs):
        orb.on_passive()


def _trigger_leftmost_orb_passive(player, timing: str) -> None:
    orbs = list(player.orb_manager.orbs)
    if not orbs:
        return
    orb = orbs[0]
    if getattr(orb, "passive_timing", None) == timing:
        orb.on_passive()


@register("relic")
class CrackedCore(Relic):
    """At the start of each combat, Channel 1 Lightning."""

    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON

    def on_combat_start(self, floor: int):
        add_action(AddOrbAction(LightningOrb()))


@register("relic")
class DataDisk(Relic):
    """Start each combat with 1 Focus."""

    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON

    def on_combat_start(self, floor: int):
        from engine.game_state import game_state
        player = game_state.player
        if player is None:
            return
        add_action(ApplyPowerAction(FocusPower(amount=1, owner=player), player))


@register("relic")
class GoldPlatedCables(Relic):
    """Your leftmost Orb triggers its passive an additional time."""

    def __init__(self):
        super().__init__()
        self.rarity = RarityType.UNCOMMON

    def on_player_turn_start(self):
        from engine.game_state import game_state
        player = game_state.player
        if player is None:
            return
        _trigger_leftmost_orb_passive(player, timing="turn_start")

    def on_player_turn_end(self):
        from engine.game_state import game_state
        player = game_state.player
        if player is None:
            return
        _trigger_leftmost_orb_passive(player, timing="turn_end")


@register("relic")
class SymbioticVirus(Relic):
    """At the start of each combat, Channel 1 Dark."""

    def __init__(self):
        super().__init__()
        self.rarity = RarityType.UNCOMMON

    def on_combat_start(self, floor: int):
        add_action(AddOrbAction(DarkOrb()))


@register("relic")
class EmotionChip(Relic):
    """If you lost HP during the previous turn, trigger the passive ability of all Orbs at the start of your turn."""

    def __init__(self):
        super().__init__()
        self.rarity = RarityType.RARE
        self._lost_hp_since_last_turn = False

    def on_combat_start(self, floor: int):
        self._lost_hp_since_last_turn = False

    def on_any_hp_lost(self, amount, source=None, card=None):
        if amount > 0:
            self._lost_hp_since_last_turn = True

    def on_player_turn_start(self):
        if not self._lost_hp_since_last_turn:
            return
        self._lost_hp_since_last_turn = False
        from engine.game_state import game_state
        player = game_state.player
        if player is None:
            return
        _trigger_all_orb_passives(player)


@register("relic")
class FrozenCore(Relic):
    """If you end your turn with any empty Orb slots, channel 1 Frost."""

    def __init__(self):
        super().__init__()
        self.rarity = RarityType.BOSS

    def on_player_turn_end(self):
        from engine.game_state import game_state
        player = game_state.player
        if player is None:
            return
        if len(player.orb_manager.orbs) < player.orb_manager.max_orb_slots:
            add_action(AddOrbAction(FrostOrb()))


@register("relic")
class Inserter(Relic):
    """Every 2 turns, gain 1 Orb slot."""

    def __init__(self):
        super().__init__()
        self.rarity = RarityType.BOSS
        self.counter = 0

    def on_combat_start(self, floor: int):
        self.counter = 0

    def on_player_turn_start(self):
        self.counter += 1
        if self.counter % 2 == 0:
            add_action(IncreaseOrbSlotsAction(amount=1))


@register("relic")
class NuclearBattery(Relic):
    """At the start of each combat, Channel 1 Plasma."""

    def __init__(self):
        super().__init__()
        self.rarity = RarityType.BOSS

    def on_combat_start(self, floor: int):
        add_action(AddOrbAction(PlasmaOrb()))


@register("relic")
class RunicCapacitor(Relic):
    """Start each combat with 3 additional Orb slots."""

    def __init__(self):
        super().__init__()
        self.rarity = RarityType.SHOP
        self._activated_this_combat = False

    def on_combat_start(self, floor: int):
        self._activated_this_combat = False

    def on_player_turn_start(self):
        if self._activated_this_combat:
            return
        self._activated_this_combat = True
        add_action(IncreaseOrbSlotsAction(amount=3))
