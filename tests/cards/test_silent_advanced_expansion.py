from cards.silent.adrenaline import Adrenaline
from cards.silent.all_out_attack import AllOutAttack
from cards.silent.caltrops import Caltrops
from cards.silent.choke import Choke
from cards.silent.crippling_cloud import CripplingCloud
from cards.silent.die_die_die import DieDieDie
from cards.silent.piercing_wail import PiercingWail
from cards.silent.riddle_with_holes import RiddleWithHoles
from cards.ironclad.strike import Strike
from enemies.act1.cultist import Cultist
from powers.definitions.poison import PoisonPower
from tests.test_combat_utils import create_test_helper
from utils.types import PilePosType


class TestSilentAdvancedExpansion:
    def setup_method(self):
        self.helper = create_test_helper()
        self.player = self.helper.create_player(hp=70, max_hp=70, energy=3)

    def test_adrenaline_draws_cards_and_gains_energy(self):
        self.player.max_energy = 5
        self.player.energy = 3
        self.helper.start_combat([])
        self.player.card_manager.get_pile('draw_pile').clear()
        self.player.card_manager.add_to_pile(Strike(), 'draw_pile', PilePosType.TOP)
        self.player.card_manager.add_to_pile(Strike(), 'draw_pile', PilePosType.TOP)
        card = Adrenaline()
        self.helper.add_card_to_hand(card)
        assert self.helper.play_card(card)
        assert self.player.energy == 4
        assert len(self.player.card_manager.get_pile('hand')) == 2
        assert card in self.player.card_manager.get_pile('exhaust_pile')

    def test_all_out_attack_hits_all_enemies_and_discards_random_other_card(self, monkeypatch):
        enemy_a = self.helper.create_enemy(Cultist, hp=40)
        enemy_b = self.helper.create_enemy(Cultist, hp=40)
        self.helper.start_combat([enemy_a, enemy_b])
        keeper = Strike()
        monkeypatch.setattr('random.choice', lambda seq: keeper)
        card = AllOutAttack()
        self.helper.add_card_to_hand(card)
        self.helper.add_card_to_hand(keeper)
        assert self.helper.play_card(card)
        assert enemy_a.hp == 30
        assert enemy_b.hp == 30
        assert keeper in self.player.card_manager.get_pile('discard_pile')

    def test_caltrops_applies_thorns_like_power(self):
        self.helper.start_combat([])
        card = Caltrops()
        self.helper.add_card_to_hand(card)
        assert self.helper.play_card(card)
        thorns = self.player.get_power('Thorns')
        assert thorns is not None
        assert thorns.amount == 3

    def test_choke_applies_followup_damage_this_turn(self):
        enemy = self.helper.create_enemy(Cultist, hp=50)
        self.helper.start_combat([enemy])
        card = Choke()
        self.helper.add_card_to_hand(card)
        assert self.helper.play_card(card, target=enemy)
        assert enemy.hp == 38
        choke = enemy.get_power('Choke')
        assert choke is not None
        choke.on_card_play(Strike(), [enemy])
        self.helper.game_state.drive_actions()
        assert enemy.hp == 35

    def test_crippling_cloud_applies_weak_and_poison_to_all_enemies(self):
        enemy_a = self.helper.create_enemy(Cultist, hp=40)
        enemy_b = self.helper.create_enemy(Cultist, hp=40)
        self.helper.start_combat([enemy_a, enemy_b])
        card = CripplingCloud()
        self.helper.add_card_to_hand(card)
        assert self.helper.play_card(card)
        for enemy in (enemy_a, enemy_b):
            weak = enemy.get_power('Weak')
            poison = enemy.get_power('Poison')
            assert weak is not None
            assert weak.amount == 2
            assert poison is not None
            assert poison.amount == 4
        assert card in self.player.card_manager.get_pile('exhaust_pile')

    def test_die_die_die_damages_all_and_exhausts(self):
        enemy_a = self.helper.create_enemy(Cultist, hp=30)
        enemy_b = self.helper.create_enemy(Cultist, hp=30)
        self.helper.start_combat([enemy_a, enemy_b])
        card = DieDieDie()
        self.helper.add_card_to_hand(card)
        assert self.helper.play_card(card)
        assert enemy_a.hp == 17
        assert enemy_b.hp == 17
        assert card in self.player.card_manager.get_pile('exhaust_pile')

    def test_piercing_wail_reduces_enemy_strength_temporarily(self):
        enemy = self.helper.create_enemy(Cultist, hp=40)
        self.helper.start_combat([enemy])
        card = PiercingWail()
        self.helper.add_card_to_hand(card)
        assert self.helper.play_card(card)
        strength = enemy.get_power('Strength')
        down = enemy.get_power('Strength Up')
        assert strength is not None
        assert strength.amount == -6
        assert down is not None
        assert down.amount == 6
        down.on_turn_end()
        self.helper.game_state.drive_actions()
        strength = enemy.get_power('Strength')
        assert strength is not None
        assert strength.amount == 0

    def test_riddle_with_holes_hits_five_times(self):
        enemy = self.helper.create_enemy(Cultist, hp=40)
        self.helper.start_combat([enemy])
        card = RiddleWithHoles()
        self.helper.add_card_to_hand(card)
        assert self.helper.play_card(card, target=enemy)
        assert enemy.hp == 25
