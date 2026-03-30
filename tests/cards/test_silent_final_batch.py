from cards.silent.bullet_time import BulletTime
from cards.silent.burst import Burst
from cards.silent.calculated_gamble import CalculatedGamble
from cards.silent.corpse_explosion import CorpseExplosion
from cards.silent.doppelganger import Doppelganger
from cards.silent.grand_finale import GrandFinale
from cards.silent.malaise import Malaise
from cards.silent.masterful_stab import MasterfulStab
from cards.silent.nightmare import Nightmare
from cards.silent.setup import Setup
from cards.silent.storm_of_steel import StormOfSteel
from cards.silent.tools_of_the_trade import ToolsOfTheTrade
from cards.silent.unload import Unload
from cards.silent.well_laid_plans import WellLaidPlans
from cards.silent.blur import Blur
from actions.card import ChooseCardLambdaAction
from cards.ironclad.strike import Strike
from enemies.act1.cultist import Cultist
from tests.test_combat_utils import create_test_helper
from utils.types import PilePosType


class TestSilentFinalBatch:
    def setup_method(self):
        self.helper = create_test_helper()
        self.player = self.helper.create_player(hp=70, max_hp=70, energy=3, max_energy=10)
        self.player.namespace = 'silent'

    def test_bullet_time_sets_hand_costs_to_zero_and_prevents_draw(self):
        self.helper.start_combat([])
        a = Strike()
        b = Blur()
        self.helper.add_card_to_hand(a)
        self.helper.add_card_to_hand(b)
        self.player.card_manager.add_to_pile(Strike(), 'draw_pile', PilePosType.TOP)
        card = BulletTime()
        self.helper.add_card_to_hand(card)
        assert self.helper.play_card(card)
        assert a.cost == 0
        assert b.cost == 0
        hand_before = len(self.player.card_manager.get_pile('hand'))
        from actions.card import DrawCardsAction
        DrawCardsAction(count=1).execute()
        self.helper.game_state.drive_actions()
        assert len(self.player.card_manager.get_pile('hand')) == hand_before

    def test_burst_replays_next_skill(self):
        enemy = self.helper.create_enemy(Cultist, hp=40)
        self.helper.start_combat([enemy])
        burst = Burst()
        blur = Blur()
        self.helper.add_card_to_hand(burst)
        self.helper.add_card_to_hand(blur)
        assert self.helper.play_card(burst)
        assert self.helper.play_card(blur)
        assert self.player.block == 10

    def test_upgraded_burst_replays_next_two_skills_once_each(self):
        self.helper.start_combat([])
        burst = Burst()
        burst.upgrade()
        blur_a = Blur()
        blur_b = Blur()
        self.helper.add_card_to_hand(burst)
        self.helper.add_card_to_hand(blur_a)
        self.helper.add_card_to_hand(blur_b)
        assert self.helper.play_card(burst)
        assert self.helper.play_card(blur_a)
        assert self.player.block == 10
        assert self.helper.play_card(blur_b)
        assert self.player.block == 20

    def test_calculated_gamble_discards_hand_and_draws_same_amount(self):
        self.helper.start_combat([])
        self.player.card_manager.get_pile('draw_pile').clear()
        for _ in range(3):
            self.player.card_manager.add_to_pile(Strike(), 'draw_pile', PilePosType.TOP)
        self.helper.add_card_to_hand(Strike())
        self.helper.add_card_to_hand(Blur())
        card = CalculatedGamble()
        self.helper.add_card_to_hand(card)
        assert self.helper.play_card(card)
        assert len(self.player.card_manager.get_pile('hand')) == 2
        assert card in self.player.card_manager.get_pile('exhaust_pile')

    def test_corpse_explosion_kills_all_on_target_death(self):
        enemy_a = self.helper.create_enemy(Cultist, hp=10)
        enemy_b = self.helper.create_enemy(Cultist, hp=20)
        self.helper.start_combat([enemy_a, enemy_b])
        card = CorpseExplosion()
        self.helper.add_card_to_hand(card)
        assert self.helper.play_card(card, target=enemy_a)
        enemy_a.hp = 0
        from engine.messages import CreatureDiedMessage
        self.helper.game_state.publish_message(CreatureDiedMessage(creature=enemy_a, source=self.player))
        self.helper.game_state.drive_actions()
        assert enemy_b.hp == 10

    def test_doppelganger_grants_next_turn_energy_and_draw(self):
        self.player.energy = 3
        combat = self.helper.start_combat([])
        self.player.card_manager.get_pile('draw_pile').clear()
        for _ in range(3):
            self.player.card_manager.add_to_pile(Strike(), 'draw_pile', PilePosType.TOP)
        card = Doppelganger()
        self.helper.add_card_to_hand(card)
        assert self.helper.play_card(card)
        combat._end_player_phase()
        combat._start_player_turn()
        self.helper.game_state.drive_actions()
        assert self.player.energy == 10
        assert len(self.player.card_manager.get_pile('hand')) >= 3

    def test_grand_finale_requires_empty_draw_pile(self):
        enemy = self.helper.create_enemy(Cultist, hp=50)
        self.helper.start_combat([enemy])
        self.player.card_manager.add_to_pile(Strike(), 'draw_pile', PilePosType.TOP)
        card = GrandFinale()
        can_play, _ = card.can_play()
        assert can_play is False
        self.player.card_manager.get_pile('draw_pile').clear()
        self.helper.add_card_to_hand(card)
        assert self.helper.play_card(card)
        assert enemy.hp == 0

    def test_malaise_applies_weak_and_strength_loss_from_x(self):
        enemy = self.helper.create_enemy(Cultist, hp=40)
        self.player.energy = 3
        self.helper.start_combat([enemy])
        self.player.energy = 3
        card = Malaise()
        self.helper.add_card_to_hand(card)
        assert self.helper.play_card(card, target=enemy)
        weak = enemy.get_power('Weak')
        strength = enemy.get_power('Strength')
        assert weak is not None and weak.amount == 3
        assert strength is not None and strength.amount == -3

    def test_masterful_stab_cost_increases_when_hp_lost(self):
        self.helper.start_combat([])
        card = MasterfulStab()
        self.helper.add_card_to_hand(card)
        assert card.cost == 0
        from actions.combat import LoseHPAction
        LoseHPAction(amount=2, target=self.player).execute()
        self.helper.game_state.drive_actions()
        assert card.cost == 1

    def test_nightmare_adds_three_copies_next_turn(self):
        combat = self.helper.start_combat([])
        target = Strike()
        self.helper.add_card_to_hand(target)
        card = Nightmare()
        self.helper.add_card_to_hand(card)
        assert self.helper.play_card(card)
        combat._end_player_phase()
        combat._start_player_turn()
        self.helper.game_state.drive_actions()
        assert sum(1 for c in self.player.card_manager.get_pile('hand') if isinstance(c, Strike)) >= 3

    def test_nightmare_queues_generic_choose_card_lambda_action(self):
        self.helper.start_combat([])
        card = Nightmare()
        card.on_play([])
        queued = self.helper.game_state.action_queue.peek_next()
        assert isinstance(queued, ChooseCardLambdaAction)

    def test_setup_sets_cost_zero_until_card_is_played(self):
        combat = self.helper.start_combat([])
        target = Strike()
        target.cost_until_end_of_turn = 1
        self.helper.add_card_to_hand(target)
        card = Setup()
        self.helper.add_card_to_hand(card)
        assert self.helper.play_card(card)
        assert target in self.player.card_manager.get_pile('draw_pile')
        combat._end_player_phase()
        combat._start_player_turn()
        self.helper.game_state.drive_actions()
        assert target in self.player.card_manager.get_pile('hand')
        assert target.cost_until_end_of_turn is None
        assert target.cost == 0
        assert self.helper.play_card(target, target=None) is True
        assert target.cost == target.base_cost

    def test_cards_expose_distinct_temporary_cost_overrides(self):
        card = Strike()
        assert hasattr(card, "cost_until_played")
        assert hasattr(card, "cost_until_end_of_turn")
        assert not hasattr(card, "temp_cost")
        assert card.cost_until_played is None
        assert card.cost_until_end_of_turn is None
        card.cost_until_end_of_turn = 1
        assert card.cost_until_end_of_turn == 1
        card.cost_until_played = 0
        assert card.cost == 1

    def test_storm_of_steel_discards_hand_and_adds_shivs(self):
        self.helper.start_combat([])
        self.helper.add_card_to_hand(Strike())
        self.helper.add_card_to_hand(Blur())
        card = StormOfSteel()
        self.helper.add_card_to_hand(card)
        assert self.helper.play_card(card)
        assert len([c for c in self.player.card_manager.get_pile('hand') if c.__class__.__name__ == 'Shiv']) == 2

    def test_tools_of_the_trade_draws_then_discards_each_turn(self):
        combat = self.helper.start_combat([])
        self.player.card_manager.get_pile('draw_pile').clear()
        self.player.card_manager.add_to_pile(Strike(), 'draw_pile', PilePosType.TOP)
        card = ToolsOfTheTrade()
        self.helper.add_card_to_hand(card)
        assert self.helper.play_card(card)
        combat._end_player_phase()
        combat._start_player_turn()
        self.helper.game_state.drive_actions()
        assert len(self.player.card_manager.get_pile('discard_pile')) >= 1

    def test_unload_discards_hand_after_attack(self):
        enemy = self.helper.create_enemy(Cultist, hp=40)
        self.helper.start_combat([enemy])
        self.helper.add_card_to_hand(Strike())
        self.helper.add_card_to_hand(Blur())
        card = Unload()
        self.helper.add_card_to_hand(card)
        assert self.helper.play_card(card, target=enemy)
        assert enemy.hp == 26
        assert len(self.player.card_manager.get_pile('hand')) == 0

    def test_well_laid_plans_retains_selected_cards(self):
        combat = self.helper.start_combat([])
        keep = Strike()
        toss = Blur()
        card = WellLaidPlans()
        self.helper.add_card_to_hand(keep)
        self.helper.add_card_to_hand(toss)
        self.helper.add_card_to_hand(card)
        assert self.helper.play_card(card)
        combat._end_player_phase()
        self.helper.game_state.drive_actions()
        assert len(self.player.card_manager.get_pile('hand')) >= 1

    def test_cards_expose_explicit_retain_flags(self):
        card = Strike()
        assert hasattr(card, 'retain_this_turn')
        assert hasattr(card, 'retain_for_this_turn')
        assert card.retain_this_turn is False
        assert card.retain_for_this_turn is False
        card.retain_for_this_turn = True
        assert card.retain_this_turn is True
