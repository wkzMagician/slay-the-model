from cards.silent.neutralize import Neutralize
from enemies.act1.cultist import Cultist
from relics.character.silent import RingOfTheSnake
from tests.test_combat_utils import create_test_helper


class TestSilentStarters:
    def setup_method(self):
        self.helper = create_test_helper()
        self.player = self.helper.create_player(hp=70, max_hp=70, energy=3)

    def test_neutralize_basic_properties(self):
        card = Neutralize()
        assert card.cost == 0
        assert card.base_damage == 3
        assert card.get_magic_value("weak") == 1

    def test_neutralize_deals_damage_and_applies_weak(self):
        enemy = self.helper.create_enemy(Cultist, hp=40)
        self.helper.start_combat([enemy])

        card = Neutralize()
        self.helper.add_card_to_hand(card)

        result = self.helper.play_card(card, target=enemy)
        assert result is True
        assert enemy.hp == 37

        weak_power = next((power for power in enemy.powers if power.idstr == "WeakPower"), None)
        assert weak_power is not None
        assert weak_power.amount == 1

    def test_neutralize_upgrade_increases_damage_and_weak(self):
        enemy = self.helper.create_enemy(Cultist, hp=40)
        self.helper.start_combat([enemy])

        card = Neutralize()
        card.upgrade()
        self.helper.add_card_to_hand(card)

        result = self.helper.play_card(card, target=enemy)
        assert result is True
        assert enemy.hp == 35

        weak_power = next((power for power in enemy.powers if power.idstr == "WeakPower"), None)
        assert weak_power is not None
        assert weak_power.amount == 2

    def test_ring_of_the_snake_draws_two_cards_on_combat_start(self):
        self.player.card_manager.piles["draw_pile"] = [Neutralize(), Neutralize(), Neutralize()]
        relic = RingOfTheSnake()
        self.player.relics = [relic]

        assert len(self.player.card_manager.piles["hand"]) == 0

        relic.on_combat_start(self.player, [])
        self.helper.game_state.drive_actions()

        assert len(self.player.card_manager.piles["hand"]) == 2
        assert len(self.player.card_manager.piles["draw_pile"]) == 1
