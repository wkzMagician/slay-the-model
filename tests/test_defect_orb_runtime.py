from actions.base import LambdaAction
from actions.orb import AddOrbAction
from engine.runtime_api import add_action
from enemies.act1.cultist import Cultist
from orbs.base import Orb
from orbs.dark import DarkOrb
from orbs.frost import FrostOrb
from orbs.lightning import LightningOrb
from orbs.plasma import PlasmaOrb
from powers.definitions.focus import FocusPower
from tests.test_combat_utils import create_test_helper


class _TrackingOrb(Orb):
    def __init__(self):
        super().__init__()
        self.evoke_count = 0

    def on_evoke(self):
        add_action(LambdaAction(func=self._mark_evoke))

    def _mark_evoke(self):
        self.evoke_count += 1


class TestDefectOrbRuntime:
    def setup_method(self):
        self.helper = create_test_helper()
        self.player = self.helper.create_player(hp=75, max_hp=75, energy=3)
        self.player.namespace = "defect"

    def test_add_orb_evokes_rightmost_when_slots_are_full(self):
        self.helper.start_combat([])
        self.player.orb_manager.max_orb_slots = 1
        original = _TrackingOrb()
        self.player.orb_manager.add_orb(original)

        AddOrbAction(LightningOrb()).execute()
        self.helper.game_state.drive_actions()

        assert original.evoke_count == 1
        assert len(self.player.orb_manager.orbs) == 1
        assert isinstance(self.player.orb_manager.orbs[0], LightningOrb)

    def test_frost_passive_gains_block_for_player(self):
        enemy = self.helper.create_enemy(Cultist, hp=40)
        self.helper.start_combat([enemy])
        orb = FrostOrb()

        orb.on_passive()
        self.helper.game_state.drive_actions()

        assert self.player.block == 2
        assert enemy.block == 0

    def test_lightning_evoke_targets_single_enemy_not_list(self):
        enemy = self.helper.create_enemy(Cultist, hp=40)
        self.helper.start_combat([enemy])
        orb = LightningOrb()

        orb.on_evoke()
        self.helper.game_state.drive_actions()

        assert enemy.hp == 32

    def test_dark_focus_applies_to_passive_growth_not_double_to_evoke(self):
        enemy = self.helper.create_enemy(Cultist, hp=40)
        self.helper.start_combat([enemy])
        self.player.add_power(FocusPower(amount=1, owner=self.player))
        orb = DarkOrb()

        orb.on_passive()
        self.helper.game_state.drive_actions()

        assert orb.charge == 13

        orb.on_evoke()
        self.helper.game_state.drive_actions()

        assert enemy.hp == 27

    def test_start_player_turn_triggers_plasma_passive(self):
        combat = self.helper.start_combat([])
        self.player.max_energy = 5
        self.player.energy = 0
        self.player.orb_manager.add_orb(PlasmaOrb())

        combat._start_player_turn()
        self.helper.game_state.drive_actions()

        assert self.player.energy == 6

    def test_end_player_phase_triggers_end_of_turn_orb_passives(self):
        enemy = self.helper.create_enemy(Cultist, hp=40)
        combat = self.helper.start_combat([enemy])
        dark = DarkOrb()
        self.player.orb_manager.max_orb_slots = 3
        self.player.orb_manager.add_orb(LightningOrb())
        self.player.orb_manager.add_orb(FrostOrb())
        self.player.orb_manager.add_orb(dark)
        self.player.block = 0

        combat._end_player_phase()
        self.helper.game_state.drive_actions()

        assert enemy.hp == 37
        assert self.player.block == 2
        assert dark.charge == 12

