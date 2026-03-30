from cards.silent.acrobatics import Acrobatics
from cards.silent.backflip import Backflip
from cards.silent.bane import Bane
from cards.silent.dagger_spray import DaggerSpray
from cards.silent.poisoned_stab import PoisonedStab
from cards.ironclad.strike import Strike
from enemies.act1.cultist import Cultist
from powers.definitions.poison import PoisonPower
from tests.test_combat_utils import create_test_helper
from utils.types import PilePosType


class TestSilentPoisonAndDiscard:
    def setup_method(self):
        self.helper = create_test_helper()
        self.player = self.helper.create_player(hp=70, max_hp=70, energy=3)

    def test_bane_deals_bonus_damage_to_poisoned_enemy(self):
        enemy = self.helper.create_enemy(Cultist, hp=40)
        self.helper.start_combat([enemy])
        enemy.add_power(PoisonPower(amount=2, duration=2, owner=enemy))

        card = Bane()
        self.helper.add_card_to_hand(card)
        assert self.helper.play_card(card, target=enemy)

        assert enemy.hp == 26

    def test_poisoned_stab_deals_damage_and_applies_poison(self):
        enemy = self.helper.create_enemy(Cultist, hp=40)
        self.helper.start_combat([enemy])

        card = PoisonedStab()
        self.helper.add_card_to_hand(card)
        assert self.helper.play_card(card, target=enemy)

        assert enemy.hp == 34
        poison = next((power for power in enemy.powers if power.idstr == "PoisonPower"), None)
        assert poison is not None
        assert poison.amount == 3

    def test_dagger_spray_hits_all_enemies_twice(self):
        enemy_a = self.helper.create_enemy(Cultist, hp=30)
        enemy_b = self.helper.create_enemy(Cultist, hp=30)
        self.helper.start_combat([enemy_a, enemy_b])

        card = DaggerSpray()
        self.helper.add_card_to_hand(card)
        assert self.helper.play_card(card)

        assert enemy_a.hp == 22
        assert enemy_b.hp == 22

    def test_backflip_gains_block_and_draws_cards(self):
        self.helper.start_combat([])
        self.player.card_manager.get_pile("draw_pile").clear()
        self.player.card_manager.add_to_pile(Strike(), "draw_pile", PilePosType.TOP)
        self.player.card_manager.add_to_pile(Strike(), "draw_pile", PilePosType.TOP)

        card = Backflip()
        self.helper.add_card_to_hand(card)
        assert self.helper.play_card(card)

        assert self.player.block == 5
        assert len(self.player.card_manager.get_pile("hand")) == 2

    def test_acrobatics_draws_then_discards_one(self):
        self.helper.start_combat([])
        self.player.card_manager.get_pile("draw_pile").clear()
        self.player.card_manager.add_to_pile(Strike(), "draw_pile", PilePosType.TOP)
        self.player.card_manager.add_to_pile(Strike(), "draw_pile", PilePosType.TOP)
        self.player.card_manager.add_to_pile(Strike(), "draw_pile", PilePosType.TOP)

        filler = Strike()
        card = Acrobatics()
        self.helper.add_card_to_hand(filler)
        self.helper.add_card_to_hand(card)
        assert self.helper.play_card(card)

        assert len(self.player.card_manager.get_pile("hand")) == 3
        assert len(self.player.card_manager.get_pile("discard_pile")) == 2
