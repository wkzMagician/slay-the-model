from cards.silent.dagger_throw import DaggerThrow
from cards.silent.deflect import Deflect
from cards.silent.dodge_and_roll import DodgeAndRoll
from cards.silent.flying_knee import FlyingKnee
from cards.silent.heel_hook import HeelHook
from cards.silent.outmaneuver import Outmaneuver
from cards.silent.prepared import Prepared
from cards.silent.quick_slash import QuickSlash
from cards.silent.slice import Slice
from cards.silent.sucker_punch import SuckerPunch
from cards.ironclad.strike import Strike
from enemies.act1.cultist import Cultist
from powers.definitions.weak import WeakPower
from tests.test_combat_utils import create_test_helper
from utils.types import PilePosType


class TestSilentCommonExpansion:
    def setup_method(self):
        self.helper = create_test_helper()
        self.player = self.helper.create_player(hp=70, max_hp=70, energy=3)

    def test_dagger_throw_deals_damage_draws_and_discards(self):
        enemy = self.helper.create_enemy(Cultist, hp=40)
        self.helper.start_combat([enemy])
        self.player.card_manager.get_pile('draw_pile').clear()
        self.player.card_manager.add_to_pile(Strike(), 'draw_pile', PilePosType.TOP)
        filler = Strike()
        card = DaggerThrow()
        self.helper.add_card_to_hand(filler)
        self.helper.add_card_to_hand(card)

        assert self.helper.play_card(card, target=enemy)

        assert enemy.hp == 34
        assert len(self.player.card_manager.get_pile('hand')) == 1
        assert len(self.player.card_manager.get_pile('discard_pile')) == 2

    def test_deflect_is_zero_cost_block(self):
        self.helper.start_combat([])
        card = Deflect()
        self.helper.add_card_to_hand(card)
        assert self.helper.play_card(card)
        assert self.player.block == 4
        assert self.player.energy == 3

    def test_dodge_and_roll_grants_block_now_and_next_turn(self):
        self.helper.start_combat([])
        card = DodgeAndRoll()
        self.helper.add_card_to_hand(card)
        assert self.helper.play_card(card)
        assert self.player.block == 4
        power = self.player.get_power('Next Turn Block')
        assert power is not None
        power.on_turn_start()
        self.helper.game_state.drive_actions()
        assert self.player.block == 8

    def test_flying_knee_grants_energy_next_turn(self):
        enemy = self.helper.create_enemy(Cultist, hp=40)
        self.helper.start_combat([enemy])
        card = FlyingKnee()
        self.helper.add_card_to_hand(card)
        assert self.helper.play_card(card, target=enemy)
        assert enemy.hp == 32
        power = self.player.get_power('Energized')
        assert power is not None
        self.player.energy = 0
        power.on_turn_start()
        self.helper.game_state.drive_actions()
        assert self.player.energy == 1

    def test_heel_hook_draws_and_gains_energy_against_weak_enemy(self):
        enemy = self.helper.create_enemy(Cultist, hp=40)
        self.helper.start_combat([enemy])
        enemy.add_power(WeakPower(amount=1, duration=1, owner=enemy))
        self.player.card_manager.get_pile('draw_pile').clear()
        self.player.card_manager.add_to_pile(Strike(), 'draw_pile', PilePosType.TOP)
        card = HeelHook()
        self.helper.add_card_to_hand(card)
        assert self.helper.play_card(card, target=enemy)
        assert enemy.hp == 35
        assert self.player.energy == 3
        assert len(self.player.card_manager.get_pile('hand')) == 1

    def test_outmaneuver_grants_energy_next_turn(self):
        self.helper.start_combat([])
        card = Outmaneuver()
        self.helper.add_card_to_hand(card)
        assert self.helper.play_card(card)
        power = self.player.get_power('Energized')
        assert power is not None
        assert power.amount == 2

    def test_prepared_draws_then_discards(self):
        self.helper.start_combat([])
        self.player.card_manager.get_pile('draw_pile').clear()
        self.player.card_manager.add_to_pile(Strike(), 'draw_pile', PilePosType.TOP)
        filler_a = Strike()
        filler_b = Strike()
        card = Prepared()
        self.helper.add_card_to_hand(filler_a)
        self.helper.add_card_to_hand(filler_b)
        self.helper.add_card_to_hand(card)
        assert self.helper.play_card(card)
        assert len(self.player.card_manager.get_pile('hand')) == 1
        assert len(self.player.card_manager.get_pile('discard_pile')) == 3

    def test_quick_slash_deals_damage_and_draws(self):
        enemy = self.helper.create_enemy(Cultist, hp=40)
        self.helper.start_combat([enemy])
        self.player.card_manager.get_pile('draw_pile').clear()
        self.player.card_manager.add_to_pile(Strike(), 'draw_pile', PilePosType.TOP)
        card = QuickSlash()
        self.helper.add_card_to_hand(card)
        assert self.helper.play_card(card, target=enemy)
        assert enemy.hp == 32
        assert len(self.player.card_manager.get_pile('hand')) == 1

    def test_slice_is_zero_cost_attack(self):
        enemy = self.helper.create_enemy(Cultist, hp=40)
        self.helper.start_combat([enemy])
        card = Slice()
        self.helper.add_card_to_hand(card)
        assert self.helper.play_card(card, target=enemy)
        assert enemy.hp == 34
        assert self.player.energy == 3

    def test_sucker_punch_applies_weak(self):
        enemy = self.helper.create_enemy(Cultist, hp=40)
        self.helper.start_combat([enemy])
        card = SuckerPunch()
        self.helper.add_card_to_hand(card)
        assert self.helper.play_card(card, target=enemy)
        assert enemy.hp == 33
        weak = next((power for power in enemy.powers if power.idstr == 'WeakPower'), None)
        assert weak is not None
        assert weak.amount == 1
