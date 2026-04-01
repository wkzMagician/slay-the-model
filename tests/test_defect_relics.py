from actions.combat import DealDamageAction
from enemies.act1.cultist import Cultist
from orbs.frost import FrostOrb
from orbs.plasma import PlasmaOrb
from powers.definitions.focus import FocusPower
from relics.character.defect import (
    CrackedCore,
    DataDisk,
    EmotionChip,
    FrozenCore,
    GoldPlatedCables,
    Inserter,
    NuclearBattery,
    RunicCapacitor,
    SymbioticVirus,
)
from tests.test_combat_utils import CombatTestHelper


class TestDefectRelics:
    def setup_method(self):
        self.helper = CombatTestHelper()
        self.player = self.helper.create_player(hp=75, max_hp=75, energy=3)
        self.player.namespace = "defect"

    def test_data_disk_applies_focus_on_combat_start(self):
        self.player.relics = [DataDisk()]
        self.helper.start_combat([])
        self.helper.game_state.drive_actions()

        focus = self.player.get_power("Focus")
        assert focus is not None
        assert focus.amount == 1

    def test_symbiotic_virus_channels_dark_on_combat_start(self):
        self.player.relics = [SymbioticVirus()]
        self.helper.start_combat([])
        self.helper.game_state.drive_actions()

        assert len(self.player.orb_manager.orbs) == 1
        assert self.player.orb_manager.orbs[0].__class__.__name__ == "DarkOrb"

    def test_nuclear_battery_channels_plasma_on_combat_start(self):
        self.player.relics = [NuclearBattery()]
        self.helper.start_combat([])
        self.helper.game_state.drive_actions()

        assert len(self.player.orb_manager.orbs) == 1
        assert isinstance(self.player.orb_manager.orbs[0], PlasmaOrb)

    def test_runic_capacitor_grants_three_combat_orb_slots(self):
        self.player.relics = [RunicCapacitor()]
        self.helper.start_combat([])
        self.helper.game_state.drive_actions()

        assert self.player.base_orb_slots == 1
        assert self.player.orb_manager.max_orb_slots == 4

    def test_gold_plated_cables_triggers_rightmost_orb_additional_time(self):
        self.player.relics = [GoldPlatedCables()]
        combat = self.helper.start_combat([])
        self.player.orb_manager.add_orb(FrostOrb())
        self.player.block = 0

        combat._end_player_phase()
        self.helper.game_state.drive_actions()

        assert self.player.block == 4

    def test_emotion_chip_triggers_all_orb_passives_after_losing_hp(self):
        enemy = self.helper.create_enemy(Cultist, hp=40)
        self.player.relics = [EmotionChip()]
        combat = self.helper.start_combat([enemy])
        self.player.block = 0
        self.player.orb_manager.max_orb_slots = 2
        self.player.orb_manager.add_orb(FrostOrb())
        self.player.orb_manager.add_orb(PlasmaOrb())
        self.player.energy = 0

        DealDamageAction(damage=4, target=self.player, source=enemy).execute()
        self.helper.game_state.drive_actions()
        combat._start_player_turn()
        self.helper.game_state.drive_actions()

        assert self.player.block == 2
        assert self.player.energy == self.player.max_energy + 2

    def test_frozen_core_channels_frost_when_turn_ends_with_empty_slot(self):
        self.player.relics = [FrozenCore()]
        combat = self.helper.start_combat([])
        self.player.orb_manager.max_orb_slots = 3

        combat._end_player_phase()
        self.helper.game_state.drive_actions()

        assert len(self.player.orb_manager.orbs) == 1
        assert isinstance(self.player.orb_manager.orbs[0], FrostOrb)

    def test_inserter_gains_one_orb_slot_every_two_turns(self):
        self.player.relics = [Inserter()]
        combat = self.helper.start_combat([])

        combat._start_player_turn()
        self.helper.game_state.drive_actions()
        assert self.player.orb_manager.max_orb_slots == 1

        combat._start_player_turn()
        self.helper.game_state.drive_actions()
        assert self.player.orb_manager.max_orb_slots == 2

    def test_combat_start_resets_orbs_and_orb_slots_to_base_value(self):
        self.player.base_orb_slots = 1
        self.player.orb_manager.max_orb_slots = 5
        self.player.orb_manager.add_orb(FrostOrb())
        self.player.orb_manager.add_orb(FrostOrb())

        self.helper.start_combat([])

        assert self.player.orb_manager.max_orb_slots == 1
        assert self.player.orb_manager.orbs == []
