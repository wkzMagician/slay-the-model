from cards.silent.endless_agony import EndlessAgony
from cards.silent.escape_plan import EscapePlan
from cards.silent.phantasmal_killer import PhantasmalKiller
from cards.silent.reflex import Reflex
from cards.silent.tactician import Tactician
from cards.silent.wraith_form import WraithForm
from cards.ironclad.strike import Strike
from enemies.act1.cultist import Cultist
from tests.test_combat_utils import create_test_helper
from utils.types import PilePosType


class TestSilentTriggerAndBurstExpansion:
    def setup_method(self):
        self.helper = create_test_helper()
        self.player = self.helper.create_player(hp=70, max_hp=70, energy=3)
        self.player.namespace = 'silent'

    def test_endless_agony_adds_copy_when_drawn(self):
        self.helper.start_combat([])
        self.player.card_manager.get_pile('hand').clear()
        self.player.card_manager.get_pile('draw_pile').clear()
        card = EndlessAgony()
        self.player.card_manager.add_to_pile(card, 'draw_pile', PilePosType.TOP)
        self.helper.game_state.current_combat._start_player_turn()
        self.helper.game_state.drive_actions()
        hand = self.player.card_manager.get_pile('hand')
        assert sum(1 for c in hand if isinstance(c, EndlessAgony)) == 2

    def test_reflex_draws_cards_when_discarded(self):
        self.helper.start_combat([])
        self.player.card_manager.get_pile('draw_pile').clear()
        self.player.card_manager.add_to_pile(Strike(), 'draw_pile', PilePosType.TOP)
        self.player.card_manager.add_to_pile(Strike(), 'draw_pile', PilePosType.TOP)
        card = Reflex()
        self.helper.add_card_to_hand(card)
        self.helper.game_state.player.card_manager.move_to(card, 'discard_pile', src='hand')
        card.on_discard()
        self.helper.game_state.drive_actions()
        assert len(self.player.card_manager.get_pile('hand')) == 2

    def test_tactician_gains_energy_when_discarded(self):
        self.player.max_energy = 5
        self.player.energy = 3
        self.helper.start_combat([])
        card = Tactician()
        self.helper.add_card_to_hand(card)
        self.helper.game_state.player.card_manager.move_to(card, 'discard_pile', src='hand')
        card.on_discard()
        self.helper.game_state.drive_actions()
        assert self.player.energy == 4

    def test_escape_plan_gains_block_if_next_draw_is_skill(self):
        self.helper.start_combat([])
        self.player.card_manager.get_pile('draw_pile').clear()
        self.player.card_manager.add_to_pile(EscapePlan(), 'draw_pile', PilePosType.TOP)
        card = EscapePlan()
        self.helper.add_card_to_hand(card)
        assert self.helper.play_card(card)
        assert self.player.block == 3

    def test_wraith_form_grants_intangible_and_dexterity_down(self):
        self.helper.start_combat([])
        card = WraithForm()
        self.helper.add_card_to_hand(card)
        assert self.helper.play_card(card)
        intangible = self.player.get_power('Intangible')
        down = self.player.get_power('Dexterity Down')
        assert intangible is not None
        assert intangible.amount == 2
        assert down is not None
        assert down.amount == 1

    def test_phantasmal_killer_doubles_attack_damage_next_turn(self):
        enemy = self.helper.create_enemy(Cultist, hp=40)
        combat = self.helper.start_combat([enemy])
        card = PhantasmalKiller()
        self.helper.add_card_to_hand(card)
        assert self.helper.play_card(card)
        combat._end_player_phase()
        combat._start_player_turn()
        self.helper.game_state.drive_actions()
        strike = Strike()
        self.helper.add_card_to_hand(strike)
        assert self.helper.play_card(strike, target=enemy)
        assert enemy.hp == 28
