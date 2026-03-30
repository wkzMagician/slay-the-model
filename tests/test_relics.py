import unittest

from actions.combat import ApplyPowerAction
from enemies.act1.cultist import Cultist
from powers.definitions.poison import PoisonPower
from relics.character.ironclad import BurningBlood
from relics.character.silent import (
    NinjaScroll,
    RingOfTheSerpent,
    RingOfTheSnake,
    SneckoSkull,
)
from tests.test_combat_utils import CombatTestHelper


class TestRelics(unittest.TestCase):
    """Test relic functionality."""

    def setUp(self):
        self.helper = CombatTestHelper()
        self.player = self.helper.create_player(energy=3)
        self.helper.start_combat([])

    def test_burning_blood_creation(self):
        relic = BurningBlood()
        self.assertIsInstance(relic, BurningBlood)

    def test_relic_has_idstr(self):
        relic = BurningBlood()
        self.assertIsNotNone(relic.idstr)

    def test_ring_of_the_snake_creation(self):
        relic = RingOfTheSnake()
        self.assertIsInstance(relic, RingOfTheSnake)
        self.assertEqual(relic.idstr, "RingOfTheSnake")

    def test_ring_of_the_serpent_creation(self):
        relic = RingOfTheSerpent()
        self.assertIsInstance(relic, RingOfTheSerpent)
        self.assertEqual(relic.idstr, "RingOfTheSerpent")

    def test_ninja_scroll_adds_three_shivs(self):
        relic = NinjaScroll()
        self.player.relics = [relic]
        self.player.card_manager.piles["hand"] = []

        relic.on_combat_start(self.player, [])
        self.helper.game_state.drive_actions()

        shivs = [card for card in self.player.card_manager.piles["hand"] if card.__class__.__name__ == "Shiv"]
        self.assertEqual(len(shivs), 3)

    def test_snecko_skull_adds_extra_poison(self):
        enemy = self.helper.create_enemy(Cultist, hp=30)
        self.helper.start_combat([enemy])
        self.player.relics = [SneckoSkull()]

        ApplyPowerAction(PoisonPower(amount=5, duration=5, owner=enemy), enemy).execute()
        self.helper.game_state.drive_actions()

        poison = next((power for power in enemy.powers if power.idstr == "PoisonPower"), None)
        self.assertIsNotNone(poison)
        assert poison is not None
        self.assertEqual(poison.amount, 6)


if __name__ == "__main__":
    unittest.main()
