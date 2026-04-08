from cards.silent.backstab import Backstab
from cards.silent.bouncing_flask import BouncingFlask
from cards.silent.catalyst import Catalyst
from cards.silent.dash import Dash
from cards.silent.footwork import Footwork
from cards.silent.leg_sweep import LegSweep
from cards.silent.predator import Predator
from cards.ironclad.strike import Strike
from enemies.act1.cultist import Cultist
from powers.definitions.poison import PoisonPower
from tests.test_combat_utils import create_test_helper
from utils.types import PilePosType


class TestSilentUncommonExpansion:
    def setup_method(self):
        self.helper = create_test_helper()
        self.player = self.helper.create_player(hp=70, max_hp=70, energy=3)

    def test_backstab_is_innate_zero_cost_attack(self):
        enemy = self.helper.create_enemy(Cultist, hp=40)
        self.helper.start_combat([enemy])
        card = Backstab()
        self.helper.add_card_to_hand(card)
        assert card.innate is True
        assert self.helper.play_card(card, target=enemy)
        assert enemy.hp == 29
        assert self.player.energy == 3

    def test_dash_deals_damage_and_gains_block(self):
        enemy = self.helper.create_enemy(Cultist, hp=40)
        self.helper.start_combat([enemy])
        card = Dash()
        self.helper.add_card_to_hand(card)
        assert self.helper.play_card(card, target=enemy)
        assert enemy.hp == 30
        assert self.player.block == 10

    def test_footwork_grants_dexterity(self):
        self.helper.start_combat([])
        card = Footwork()
        self.helper.add_card_to_hand(card)
        assert self.helper.play_card(card)
        dex = self.player.get_power('Dexterity')
        assert dex is not None
        assert dex.amount == 2

    def test_leg_sweep_applies_weak_and_gains_block(self):
        enemy = self.helper.create_enemy(Cultist, hp=40)
        self.helper.start_combat([enemy])
        card = LegSweep()
        self.helper.add_card_to_hand(card)
        assert self.helper.play_card(card, target=enemy)
        assert self.player.block == 11
        weak = enemy.get_power('Weak')
        assert weak is not None
        assert weak.amount == 2

    def test_bouncing_flask_applies_poison(self):
        enemy = self.helper.create_enemy(Cultist, hp=40)
        self.helper.start_combat([enemy])
        card = BouncingFlask()
        self.helper.add_card_to_hand(card)
        assert self.helper.play_card(card, target=enemy)
        poison = enemy.get_power('Poison')
        assert poison is not None
        assert poison.amount == 9

    def test_catalyst_doubles_poison(self):
        enemy = self.helper.create_enemy(Cultist, hp=40)
        self.helper.start_combat([enemy])
        enemy.add_power(PoisonPower(amount=5, duration=5, owner=enemy))
        card = Catalyst()
        self.helper.add_card_to_hand(card)
        assert self.helper.play_card(card, target=enemy)
        poison = enemy.get_power('Poison')
        assert poison is not None
        assert poison.amount == 10

    def test_predator_adds_next_turn_draw(self):
        enemy = self.helper.create_enemy(Cultist, hp=40)
        self.helper.start_combat([enemy])
        self.player.card_manager.get_pile('draw_pile').clear()
        self.player.card_manager.add_to_pile(Strike(), 'draw_pile', PilePosType.TOP)
        self.player.card_manager.add_to_pile(Strike(), 'draw_pile', PilePosType.TOP)
        card = Predator()
        self.helper.add_card_to_hand(card)
        assert self.helper.play_card(card, target=enemy)
        assert enemy.hp == 25
        power = self.player.get_power('Draw Card Next Turn')
        assert power is not None
        assert power.amount == 2
        power.on_turn_start_post_draw()
        self.helper.game_state.drive_actions()
        assert len(self.player.card_manager.get_pile('hand')) == 2
