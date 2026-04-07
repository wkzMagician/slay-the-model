from cards.defect.aggregate import Aggregate
from cards.defect.auto_shields import AutoShields
from cards.defect.ball_lightning import BallLightning
from cards.defect.barrage import Barrage
from cards.defect.blizzard import Blizzard
from cards.defect.boot_sequence import BootSequence
from cards.defect.bullseye import Bullseye
from cards.defect.charge_battery import ChargeBattery
from cards.defect.claw import Claw
from cards.defect.cold_snap import ColdSnap
from cards.defect.compile_driver import CompileDriver
from cards.defect.coolheaded import Coolheaded
from cards.defect.darkness import Darkness
from cards.defect.defragment import Defragment
from cards.defect.doom_and_gloom import DoomAndGloom
from cards.defect.equilibrium import Equilibrium
from engine.messages import PlayerTurnEndedMessage
from engine.runtime_api import publish_message
from cards.defect.force_field import ForceField
from cards.defect.genetic_algorithm import GeneticAlgorithm
from cards.defect.glacier import Glacier
from cards.defect.melter import Melter
from cards.defect.reinforced_body import ReinforcedBody
from cards.defect.scrape import Scrape
from cards.defect.stack import Stack
from cards.defect.steam_barrier import SteamBarrier
from cards.defect.streamline import Streamline
from cards.defect.sunder import Sunder
from cards.defect.sweeping_beam import SweepingBeam
from cards.defect.tempest import Tempest
from cards.defect.thunder_strike import ThunderStrike
from cards.defect.strike import Strike
from enemies.base import Enemy
from orbs.dark import DarkOrb
from orbs.frost import FrostOrb
from orbs.lightning import LightningOrb
from powers.definitions.lock_on import LockOnPower
from relics.global_relics.shop import ChemicalX
from tests.test_combat_utils import create_test_helper
from utils.types import PilePosType


class _NoOpEnemy(Enemy):
    def __init__(self, hp: int = 40):
        super().__init__(max_hp=hp, name="Target Dummy")

    def determine_next_intention(self, floor: int = 1):
        class _Intent:
            name = "Idle"
            description = "Idle"

            def execute(self):
                return None

        return _Intent()


class TestDefectCommonCluster:
    def setup_method(self):
        self.helper = create_test_helper()
        self.player = self.helper.create_player(hp=75, max_hp=75, energy=5)
        self.player.namespace = "defect"
        self.player.base_orb_slots = 3
        self.player.orb_manager.max_orb_slots = 3

    def test_ball_lightning_deals_damage_and_channels_lightning(self):
        enemy = _NoOpEnemy(hp=30)
        self.helper.start_combat([enemy])
        card = BallLightning()
        self.helper.add_card_to_hand(card)

        assert self.helper.play_card(card, enemy) is True
        assert enemy.hp == 23
        assert isinstance(self.player.orb_manager.orbs[-1], LightningOrb)

    def test_barrage_hits_once_per_orb(self):
        enemy = _NoOpEnemy(hp=30)
        self.helper.start_combat([enemy])
        self.player.orb_manager.add_orb(LightningOrb())
        self.player.orb_manager.add_orb(FrostOrb())
        card = Barrage()
        self.helper.add_card_to_hand(card)

        assert card.attack_times == 2
        assert self.helper.play_card(card, enemy) is True
        assert enemy.hp == 22

    def test_blizzard_damage_tracks_frost_history(self):
        enemy = _NoOpEnemy(hp=40)
        combat = self.helper.start_combat([enemy])
        combat.combat_state.orb_history["Frost"] = 3
        card = Blizzard()
        self.helper.add_card_to_hand(card)

        assert card.damage == 6
        assert self.helper.play_card(card) is True
        assert enemy.hp == 34

    def test_charge_battery_grants_next_turn_energy(self):
        self.helper.start_combat([_NoOpEnemy()])
        combat = self.helper.game_state.current_combat
        assert combat is not None
        card = ChargeBattery()
        self.helper.add_card_to_hand(card)

        assert self.helper.play_card(card) is True
        self.player.energy = 0
        combat._start_player_turn()
        self.helper.game_state.drive_actions()

        assert self.player.energy >= 1

    def test_equilibrium_retains_hand_at_turn_end_including_cards_drawn_after_play(self):
        enemy = _NoOpEnemy()
        self.helper.start_combat([enemy])
        equilibrium = Equilibrium()
        strike = Strike()
        drawn_later = Strike()
        self.helper.add_card_to_hand(equilibrium)
        self.helper.add_card_to_hand(strike)

        assert self.helper.play_card(equilibrium) is True
        self.helper.game_state.drive_actions()

        assert strike.retain_this_turn is False
        self.helper.add_card_to_hand(drawn_later)

        publish_message(
            PlayerTurnEndedMessage(
                owner=self.player,
                enemies=[enemy],
                hand_cards=list(self.player.card_manager.get_pile("hand")),
            )
        )
        self.helper.game_state.drive_actions()

        assert strike.retain_this_turn is True
        assert drawn_later.retain_this_turn is True
        assert equilibrium.retain_this_turn is False
        assert not any(p.name == "Equilibrium" for p in self.player.powers)

    def test_equilibrium_does_not_mark_ethereal_for_retain_at_turn_end(self):
        enemy = _NoOpEnemy()
        self.helper.start_combat([enemy])
        eq = Equilibrium()
        ghost = Strike()
        ghost._ethereal = True
        self.helper.add_card_to_hand(eq)
        self.helper.add_card_to_hand(ghost)
        assert self.helper.play_card(eq) is True
        self.helper.game_state.drive_actions()
        publish_message(
            PlayerTurnEndedMessage(
                owner=self.player,
                enemies=[enemy],
                hand_cards=list(self.player.card_manager.get_pile("hand")),
            )
        )
        self.helper.game_state.drive_actions()
        assert ghost.retain_this_turn is False

    def test_claw_scales_other_claws(self):
        enemy = _NoOpEnemy(hp=30)
        self.helper.start_combat([enemy])
        first = Claw()
        second = Claw()
        self.helper.add_card_to_hand(first)
        self.helper.add_card_to_hand(second)

        assert self.helper.play_card(first, enemy) is True
        assert second.damage == 5

    def test_cold_snap_channels_frost(self):
        enemy = _NoOpEnemy(hp=30)
        self.helper.start_combat([enemy])
        card = ColdSnap()
        self.helper.add_card_to_hand(card)

        assert self.helper.play_card(card, enemy) is True
        assert isinstance(self.player.orb_manager.orbs[-1], FrostOrb)

    def test_compile_driver_draws_for_unique_orbs(self):
        enemy = _NoOpEnemy(hp=30)
        self.helper.start_combat([enemy])
        self.player.orb_manager.add_orb(LightningOrb())
        self.player.orb_manager.add_orb(FrostOrb())
        self.player.orb_manager.add_orb(DarkOrb())
        card = CompileDriver()
        self.helper.add_card_to_hand(card)
        self.helper.add_card_to_draw_pile(Claw())
        self.helper.add_card_to_draw_pile(Claw())
        self.helper.add_card_to_draw_pile(Claw())

        hand_before = len(self.player.card_manager.get_pile("hand"))
        assert card.draw == 3
        assert self.helper.play_card(card, enemy) is True

        assert len(self.player.card_manager.get_pile("hand")) >= hand_before + 2

    def test_coolheaded_channels_frost_and_draws(self):
        self.helper.start_combat([_NoOpEnemy()])
        card = Coolheaded()
        self.helper.add_card_to_hand(card)
        self.helper.add_card_to_draw_pile(Claw())

        hand_before = len(self.player.card_manager.get_pile("hand"))
        assert self.helper.play_card(card) is True

        assert isinstance(self.player.orb_manager.orbs[-1], FrostOrb)
        assert len(self.player.card_manager.get_pile("hand")) >= hand_before

    def test_stack_counts_discard_pile(self):
        self.helper.start_combat([_NoOpEnemy()])
        self.helper.add_card_to_discard_pile(Claw())
        self.helper.add_card_to_discard_pile(Claw())
        card = Stack()
        self.helper.add_card_to_hand(card)

        assert card.block == 2
        assert self.helper.play_card(card) is True
        assert self.player.block == 2

    def test_upgraded_stack_includes_bonus_in_dynamic_block(self):
        self.helper.start_combat([_NoOpEnemy()])
        self.helper.add_card_to_discard_pile(Claw())
        self.helper.add_card_to_discard_pile(Claw())
        card = Stack()
        card.upgrade()

        assert card.block == 5

    def test_streamline_reduces_its_own_cost(self):
        enemy = _NoOpEnemy(hp=40)
        self.helper.start_combat([enemy])
        card = Streamline()
        self.helper.add_card_to_hand(card)

        assert card.cost == 2
        assert self.helper.play_card(card, enemy) is True
        assert card.cost == 1

    def test_sweeping_beam_hits_all_and_draws(self):
        enemy_a = _NoOpEnemy(hp=20)
        enemy_b = _NoOpEnemy(hp=20)
        self.helper.start_combat([enemy_a, enemy_b])
        card = SweepingBeam()
        self.helper.add_card_to_hand(card)
        self.helper.add_card_to_draw_pile(Claw())

        assert self.helper.play_card(card) is True
        assert enemy_a.hp == 14
        assert enemy_b.hp == 14

    def test_auto_shields_only_works_without_block(self):
        self.helper.start_combat([_NoOpEnemy()])
        card = AutoShields()
        self.helper.add_card_to_hand(card)
        self.player.block = 1

        assert self.helper.play_card(card) is True
        assert self.player.block == 1

    def test_bullseye_applies_lock_on(self):
        enemy = _NoOpEnemy(hp=30)
        self.helper.start_combat([enemy])
        card = Bullseye()
        self.helper.add_card_to_hand(card)

        assert self.helper.play_card(card, enemy) is True
        assert isinstance(enemy.get_power("Lock-On"), LockOnPower)

    def test_doom_and_gloom_channels_dark(self):
        enemy_a = _NoOpEnemy(hp=30)
        enemy_b = _NoOpEnemy(hp=30)
        self.helper.start_combat([enemy_a, enemy_b])
        card = DoomAndGloom()
        self.helper.add_card_to_hand(card)

        assert self.helper.play_card(card) is True
        assert isinstance(self.player.orb_manager.orbs[-1], DarkOrb)

    def test_glacier_channels_two_frost(self):
        self.helper.start_combat([_NoOpEnemy()])
        card = Glacier()
        self.helper.add_card_to_hand(card)

        assert self.helper.play_card(card) is True
        assert len(self.player.orb_manager.orbs) == 2
        assert all(isinstance(orb, FrostOrb) for orb in self.player.orb_manager.orbs)

    def test_aggregate_scales_with_draw_pile(self):
        self.helper.start_combat([_NoOpEnemy()])
        card = Aggregate()
        self.helper.add_card_to_hand(card)
        for _ in range(8):
            self.helper.add_card_to_draw_pile(Claw())

        self.player.energy = 1
        assert self.helper.play_card(card) is True
        assert self.player.energy == 2

    def test_force_field_cost_reduces_per_power_played(self):
        self.helper.start_combat([_NoOpEnemy()])
        power_card = Defragment()
        self.helper.add_card_to_hand(power_card)
        assert self.helper.play_card(power_card) is True
        card = ForceField()
        assert card.cost == 3

    def test_steam_barrier_loses_block_after_use(self):
        self.helper.start_combat([_NoOpEnemy()])
        card = SteamBarrier()
        self.helper.add_card_to_hand(card)

        assert card.block == 6
        assert self.helper.play_card(card) is True
        assert card.block == 5

    def test_reinforced_body_uses_all_energy_for_block(self):
        self.helper.start_combat([_NoOpEnemy()])
        self.player.energy = 3
        card = ReinforcedBody()
        self.helper.add_card_to_hand(card)

        assert self.helper.play_card(card) is True
        assert self.player.block == 21

    def test_reinforced_body_gains_bonus_x_from_chemical_x(self):
        self.helper.start_combat([_NoOpEnemy()])
        self.player.energy = 3
        self.player.relics.append(ChemicalX())
        card = ReinforcedBody()
        self.helper.add_card_to_hand(card)

        assert self.helper.play_card(card) is True
        assert self.player.block == 35

    def test_tempest_channels_x_lightning(self):
        self.helper.start_combat([_NoOpEnemy()])
        self.player.energy = 3
        card = Tempest()
        self.helper.add_card_to_hand(card)

        assert self.helper.play_card(card) is True
        assert len(self.player.orb_manager.orbs) == 3

    def test_tempest_counts_chemical_x_bonus(self):
        self.helper.start_combat([_NoOpEnemy()])
        self.player.energy = 2
        self.player.relics.append(ChemicalX())
        card = Tempest()
        self.helper.add_card_to_hand(card)

        assert self.helper.play_card(card) is True
        combat = self.helper.game_state.current_combat
        assert combat is not None
        assert len(self.player.orb_manager.orbs) == 3
        assert combat.combat_state.orb_history["Lightning"] == 4

    def test_darkness_upgrade_triggers_all_dark_orb_passives_after_channel(self):
        self.helper.start_combat([_NoOpEnemy()])
        existing_dark = DarkOrb()
        self.player.orb_manager.add_orb(existing_dark)
        card = Darkness()
        card.upgrade()
        self.helper.add_card_to_hand(card)

        assert self.helper.play_card(card) is True
        assert isinstance(self.player.orb_manager.orbs[-1], DarkOrb)
        assert existing_dark.charge == 12
        assert self.player.orb_manager.orbs[-1].charge == 12

    def test_melter_removes_block_before_damage(self):
        enemy = _NoOpEnemy(hp=30)
        enemy.block = 8
        self.helper.start_combat([enemy])
        card = Melter()
        self.helper.add_card_to_hand(card)

        assert self.helper.play_card(card, enemy) is True
        assert enemy.block == 0
        assert enemy.hp == 20

    def test_scrape_discards_nonzero_cards_as_they_are_drawn(self):
        self.helper.start_combat([_NoOpEnemy()])
        self.player.card_manager.get_pile("draw_pile").clear()
        zero_card = Claw()
        costly_card = Defragment()
        self.player.card_manager.add_to_pile(costly_card, "draw_pile", PilePosType.TOP)
        self.player.card_manager.add_to_pile(zero_card, "draw_pile", PilePosType.TOP)
        card = Scrape()
        self.helper.add_card_to_hand(card)

        assert self.helper.play_card(card) is True
        hand = self.player.card_manager.get_pile("hand")
        discard = self.player.card_manager.get_pile("discard_pile")
        assert zero_card in hand
        assert costly_card in discard

    def test_sunder_refunds_energy_only_when_it_kills(self):
        enemy = _NoOpEnemy(hp=20)
        self.helper.start_combat([enemy])
        self.player.energy = 3
        card = Sunder()
        self.helper.add_card_to_hand(card)

        assert self.helper.play_card(card, enemy) is True
        assert self.player.energy == 3

    def test_thunder_strike_attack_times_tracks_lightning_history(self):
        self.helper.start_combat([_NoOpEnemy()])
        combat = self.helper.game_state.current_combat
        assert combat is not None
        combat.combat_state.orb_history["Lightning"] = 4
        card = ThunderStrike()

        assert card.attack_times == 4

    def test_genetic_algorithm_upgrades_master_deck_copy(self):
        helper = create_test_helper()
        player = helper.create_player(hp=75, max_hp=75, energy=3)
        player.namespace = "defect"
        master_card = GeneticAlgorithm()
        player.card_manager.get_pile("deck").append(master_card)
        helper.start_combat([_NoOpEnemy()])

        combat_copy = next(
            card
            for card in player.card_manager.get_pile("draw_pile")
            if isinstance(card, GeneticAlgorithm)
        )
        player.card_manager.move_to(combat_copy, "hand", "draw_pile")
        assert helper.play_card(combat_copy) is True
        assert combat_copy.block == 3
        assert master_card.block == 3
