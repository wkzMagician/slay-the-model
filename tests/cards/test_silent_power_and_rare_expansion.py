from cards.silent.after_image import AfterImage
from cards.silent.alchemize import Alchemize
from cards.silent.distraction import Distraction
from cards.silent.envenom import Envenom
from cards.silent.expertise import Expertise
from cards.silent.glass_knife import GlassKnife
from cards.silent.terror import Terror
from cards.silent.thousand_cuts import ThousandCuts
from cards.ironclad.strike import Strike
from enemies.act1.cultist import Cultist
from tests.test_combat_utils import create_test_helper
from utils.types import PilePosType


class TestSilentPowerAndRareExpansion:
    def setup_method(self):
        self.helper = create_test_helper()
        self.player = self.helper.create_player(hp=70, max_hp=70, energy=3)
        self.player.namespace = 'silent'

    def test_after_image_grants_block_when_card_is_played(self):
        self.helper.start_combat([])
        card = AfterImage()
        self.helper.add_card_to_hand(card)
        assert self.helper.play_card(card)
        assert self.player.block == 0
        power = self.player.get_power('After Image')
        assert power is not None
        power.on_card_play(Strike(), [])
        self.helper.game_state.drive_actions()
        assert self.player.block == 1

    def test_alchemize_adds_a_potion_and_exhausts(self):
        self.helper.start_combat([])
        card = Alchemize()
        self.helper.add_card_to_hand(card)
        assert self.helper.play_card(card)
        assert len(self.player.potions) == 1
        assert card in self.player.card_manager.get_pile('exhaust_pile')

    def test_distraction_queues_random_skill_choice(self):
        self.helper.start_combat([])
        card = Distraction()
        self.helper.add_card_to_hand(card)
        assert self.helper.play_card(card)
        hand = list(self.player.card_manager.get_pile('hand'))
        added = [c for c in hand if c is not card and c.__class__.__name__ != 'Strike']
        assert added
        assert any(c.card_type.name == 'SKILL' and c.cost_until_end_of_turn == 0 for c in added)
        assert card in self.player.card_manager.get_pile('exhaust_pile')

    def test_envenom_applies_poison_when_attack_deals_damage(self):
        enemy = self.helper.create_enemy(Cultist, hp=40)
        self.helper.start_combat([enemy])
        card = Envenom()
        self.helper.add_card_to_hand(card)
        assert self.helper.play_card(card)
        power = self.player.get_power('Envenom')
        assert power is not None
        power.on_damage_dealt(damage=6, target=enemy, source=self.player, card=Strike())
        self.helper.game_state.drive_actions()
        poison = enemy.get_power('Poison')
        assert poison is not None
        assert poison.amount == 1

    def test_expertise_draws_up_to_six_cards(self):
        self.helper.start_combat([])
        filler_a = Strike()
        filler_b = Strike()
        self.helper.add_card_to_hand(filler_a)
        self.helper.add_card_to_hand(filler_b)
        for _ in range(4):
            self.player.card_manager.add_to_pile(Strike(), 'draw_pile', PilePosType.TOP)
        card = Expertise()
        self.helper.add_card_to_hand(card)
        assert self.helper.play_card(card)
        assert len(self.player.card_manager.get_pile('hand')) == 6

    def test_glass_knife_deals_two_hits_and_loses_damage(self):
        enemy = self.helper.create_enemy(Cultist, hp=40)
        self.helper.start_combat([enemy])
        card = GlassKnife()
        self.helper.add_card_to_hand(card)
        assert self.helper.play_card(card, target=enemy)
        assert enemy.hp == 24
        assert card.damage == 6

    def test_terror_applies_long_vulnerable(self):
        enemy = self.helper.create_enemy(Cultist, hp=40)
        self.helper.start_combat([enemy])
        card = Terror()
        self.helper.add_card_to_hand(card)
        assert self.helper.play_card(card, target=enemy)
        vulnerable = enemy.get_power('Vulnerable')
        assert vulnerable is not None
        assert vulnerable.amount == 99

    def test_thousand_cuts_damages_all_enemies_when_card_is_played(self):
        enemy_a = self.helper.create_enemy(Cultist, hp=20)
        enemy_b = self.helper.create_enemy(Cultist, hp=20)
        self.helper.start_combat([enemy_a, enemy_b])
        card = ThousandCuts()
        self.helper.add_card_to_hand(card)
        assert self.helper.play_card(card)
        assert enemy_a.hp == 20
        assert enemy_b.hp == 20
        power = self.player.get_power('A Thousand Cuts')
        assert power is not None
        power.on_card_play(Strike(), [enemy_a, enemy_b])
        self.helper.game_state.drive_actions()
        assert enemy_a.hp == 19
        assert enemy_b.hp == 19
