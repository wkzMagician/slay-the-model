"""Comprehensive test for Reaper - AOE damage + lifesteal."""
import unittest
from cards.ironclad.reaper import Reaper
from tests.test_combat_utils import CombatTestHelper
from utils.types import CardType, RarityType

class TestReaper(unittest.TestCase):
    def setUp(self):
        self.helper = CombatTestHelper()
    def tearDown(self):
        self.helper._reset_game_state()

    def test_basic_properties(self):
        card = Reaper()
        self.assertEqual(card.cost, 2)
        self.assertEqual(card.damage, 4)
        self.assertEqual(card.card_type, CardType.ATTACK)
        self.assertEqual(card.rarity, RarityType.RARE)

    def test_deals_damage_to_all_enemies(self):
        from enemies.act1.cultist import Cultist
        self.helper.create_player(max_hp=50)
        enemy1 = self.helper.create_enemy(Cultist, hp=100)
        enemy2 = self.helper.create_enemy(Cultist, hp=100)
        self.helper.start_combat([enemy1, enemy2])
        card = Reaper()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, target=enemy1)
        # Should deal damage to all enemies (4 base)
        self.assertLess(enemy1.hp, 100)
        self.assertLess(enemy2.hp, 100)

    def test_heals_player_for_damage_dealt(self):
        from enemies.act1.cultist import Cultist
        self.helper.create_player(hp=50, max_hp=100)
        enemy = self.helper.create_enemy(Cultist, hp=100)
        self.helper.start_combat([enemy])
        card = Reaper()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, target=enemy)
        # Player should be healed (started at 50 hp)
        self.assertGreater(self.helper.get_player_hp(), 50)

    def test_upgraded(self):
        card = Reaper()
        card.upgrade()
        self.assertEqual(card.damage, 5)

    def test_energy_cost(self):
        from enemies.act1.cultist import Cultist
        self.helper.create_player()
        enemy = self.helper.create_enemy(Cultist)
        self.helper.start_combat([enemy])
        card = Reaper()
        self.assertEqual(card.cost, 2)
        self.helper.add_card_to_hand(card)
        initial_energy = self.helper.game_state.player.energy
        self.helper.play_card(card)
        self.assertEqual(self.helper.game_state.player.energy, initial_energy - 2)
