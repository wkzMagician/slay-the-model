from cards.silent.accuracy import Accuracy
from cards.silent.blade_dance import BladeDance
from cards.silent.cloak_and_dagger import CloakAndDagger
from cards.silent.deadly_poison import DeadlyPoison
from cards.silent.infinite_blades import InfiniteBlades
from cards.silent.noxious_fumes import NoxiousFumes
from cards.colorless.shiv import Shiv
from enemies.act1.cultist import Cultist
from tests.test_combat_utils import create_test_helper


class TestSilentCoreMechanics:
    def setup_method(self):
        self.helper = create_test_helper()
        self.player = self.helper.create_player(hp=70, max_hp=70, energy=3)

    def test_shiv_deals_damage_and_exhausts(self):
        enemy = self.helper.create_enemy(Cultist, hp=20)
        self.helper.start_combat([enemy])

        card = Shiv()
        self.helper.add_card_to_hand(card)

        result = self.helper.play_card(card, target=enemy)
        assert result is True
        assert enemy.hp == 16
        assert self.helper.is_card_in_exhaust("Shiv")

    def test_accuracy_increases_shiv_damage(self):
        enemy = self.helper.create_enemy(Cultist, hp=20)
        self.helper.start_combat([enemy])

        accuracy = Accuracy()
        self.helper.add_card_to_hand(accuracy)
        assert self.helper.play_card(accuracy)

        shiv = Shiv()
        self.helper.add_card_to_hand(shiv)
        assert self.helper.play_card(shiv, target=enemy)
        assert enemy.hp == 12

    def test_blade_dance_adds_three_shivs_to_hand(self):
        self.helper.start_combat([])

        card = BladeDance()
        self.helper.add_card_to_hand(card)
        assert self.helper.play_card(card)

        shivs = [c for c in self.player.card_manager.piles["hand"] if c.__class__.__name__ == "Shiv"]
        assert len(shivs) == 3

    def test_cloak_and_dagger_gains_block_and_adds_shiv(self):
        self.helper.start_combat([])

        card = CloakAndDagger()
        self.helper.add_card_to_hand(card)
        assert self.helper.play_card(card)

        assert self.player.block == 6
        shivs = [c for c in self.player.card_manager.piles["hand"] if c.__class__.__name__ == "Shiv"]
        assert len(shivs) == 1

    def test_deadly_poison_applies_poison(self):
        enemy = self.helper.create_enemy(Cultist, hp=30)
        self.helper.start_combat([enemy])

        card = DeadlyPoison()
        self.helper.add_card_to_hand(card)
        assert self.helper.play_card(card, target=enemy)

        poison = next((power for power in enemy.powers if power.idstr == "PoisonPower"), None)
        assert poison is not None
        assert poison.amount == 5

    def test_infinite_blades_adds_shiv_each_turn(self):
        self.helper.start_combat([])

        card = InfiniteBlades()
        self.helper.add_card_to_hand(card)
        assert self.helper.play_card(card)

        power = self.player.get_power("Infinite Blades")
        assert power is not None

        power.on_turn_start()
        self.helper.game_state.drive_actions()

        shivs = [c for c in self.player.card_manager.piles["hand"] if c.__class__.__name__ == "Shiv"]
        assert len(shivs) == 1

    def test_noxious_fumes_applies_poison_to_all_enemies(self):
        enemy_a = self.helper.create_enemy(Cultist, hp=30)
        enemy_b = self.helper.create_enemy(Cultist, hp=30)
        self.helper.start_combat([enemy_a, enemy_b])

        card = NoxiousFumes()
        self.helper.add_card_to_hand(card)
        assert self.helper.play_card(card)

        power = self.player.get_power("Noxious Fumes")
        assert power is not None

        power.on_turn_start()
        self.helper.game_state.drive_actions()

        for enemy in (enemy_a, enemy_b):
            poison = next((p for p in enemy.powers if p.idstr == "PoisonPower"), None)
            assert poison is not None
            assert poison.amount == 2
