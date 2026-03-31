from cards.silent.blur import Blur
from cards.silent.concentrate import Concentrate
from cards.silent.eviscerate import Eviscerate
from cards.silent.expertise import Expertise
from cards.silent.finisher import Finisher
from cards.silent.flechettes import Flechettes
from cards.silent.skewer import Skewer
from cards.silent.sneaky_strike import SneakyStrike
from cards.silent.survivor import Survivor
from cards.ironclad.strike import Strike
from enemies.act1.cultist import Cultist
from relics.global_relics.shop import ChemicalX
from tests.test_combat_utils import create_test_helper


class TestSilentCounterExpansion:
    def setup_method(self):
        self.helper = create_test_helper()
        self.player = self.helper.create_player(hp=70, max_hp=70, energy=3)
        self.player.namespace = 'silent'

    def test_blur_preserves_block_for_next_turn(self):
        enemy = self.helper.create_enemy(Cultist, hp=40)
        combat = self.helper.start_combat([enemy])
        card = Blur()
        self.helper.add_card_to_hand(card)
        assert self.helper.play_card(card)
        assert self.player.block == 5
        combat._end_player_phase()
        assert self.player.block == 5
        combat._start_player_turn()
        assert self.player.block == 5

    def test_concentrate_discards_and_gains_energy(self):
        self.player.max_energy = 5
        self.player.energy = 3
        self.helper.start_combat([])
        filler_a = Strike()
        filler_b = Strike()
        self.helper.add_card_to_hand(filler_a)
        self.helper.add_card_to_hand(filler_b)
        card = Concentrate()
        self.helper.add_card_to_hand(card)
        assert self.helper.play_card(card)
        assert self.player.energy == 5
        assert len(self.player.card_manager.get_pile('discard_pile')) >= 2

    def test_flechettes_counts_skills_in_hand(self):
        enemy = self.helper.create_enemy(Cultist, hp=40)
        self.helper.start_combat([enemy])
        self.helper.add_card_to_hand(Blur())
        self.helper.add_card_to_hand(Concentrate())
        card = Flechettes()
        self.helper.add_card_to_hand(card)
        assert card.attack_times == 2
        assert self.helper.play_card(card, target=enemy)
        assert enemy.hp == 32

    def test_finisher_counts_attacks_played_this_turn(self):
        enemy = self.helper.create_enemy(Cultist, hp=50)
        self.helper.start_combat([enemy])
        first = Strike()
        second = Strike()
        finisher = Finisher()
        self.helper.add_card_to_hand(first)
        self.helper.add_card_to_hand(second)
        self.helper.add_card_to_hand(finisher)
        assert self.helper.play_card(first, target=enemy)
        assert self.helper.play_card(second, target=enemy)
        assert finisher.attack_times == 2
        assert self.helper.play_card(finisher, target=enemy)
        assert enemy.hp == 26

    def test_sneaky_strike_refunds_energy_if_discarded_this_turn(self):
        enemy = self.helper.create_enemy(Cultist, hp=40)
        self.helper.start_combat([enemy])
        filler = Strike()
        survivor = Survivor()
        sneaky = SneakyStrike()
        self.helper.add_card_to_hand(filler)
        self.helper.add_card_to_hand(survivor)
        self.helper.add_card_to_hand(sneaky)
        assert self.helper.play_card(survivor)
        energy_before = self.player.energy
        assert self.helper.play_card(sneaky, target=enemy)
        assert self.player.energy == energy_before
        assert enemy.hp == 28

    def test_eviscerate_cost_reduces_with_discards(self):
        self.helper.start_combat([])
        filler = Strike()
        survivor = Survivor()
        card = Eviscerate()
        self.helper.add_card_to_hand(filler)
        self.helper.add_card_to_hand(survivor)
        self.helper.add_card_to_hand(card)
        assert card.cost == 3
        assert self.helper.play_card(survivor)
        assert card.cost == 2

    def test_skewer_spends_all_energy_and_hits_x_times(self):
        enemy = self.helper.create_enemy(Cultist, hp=40)
        self.player.energy = 3
        self.helper.start_combat([enemy])
        self.player.energy = 3
        card = Skewer()
        self.helper.add_card_to_hand(card)
        assert self.helper.play_card(card, target=enemy)
        assert self.player.energy == 0
        assert enemy.hp == 31

    def test_skewer_counts_chemical_x_bonus(self):
        enemy = self.helper.create_enemy(Cultist, hp=50)
        self.player.energy = 2
        self.helper.start_combat([enemy])
        self.player.energy = 2
        self.player.relics.append(ChemicalX())
        card = Skewer()
        self.helper.add_card_to_hand(card)

        assert self.helper.play_card(card, target=enemy)
        assert enemy.hp == 38

    def test_expertise_draw_property_tracks_missing_cards(self):
        self.helper.start_combat([])
        self.helper.add_card_to_hand(Strike())
        self.helper.add_card_to_hand(Strike())
        card = Expertise()
        self.helper.add_card_to_hand(card)

        assert card.draw == 3
