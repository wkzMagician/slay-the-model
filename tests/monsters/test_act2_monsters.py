"""Test Act 2 monsters"""
import unittest
from enemies.act2.book_of_stabbing import BookOfStabbing
from enemies.act2.bronze_automaton import BronzeAutomaton
from enemies.act2.bronze_orb import BronzeOrb
from enemies.act2.byrd import Byrd
from enemies.act2.centurion import Centurion
from enemies.act2.chosen import Chosen
from enemies.act2.gremlin_leader import GremlinLeader
from enemies.act2.mugger import Mugger
from enemies.act2.mystic import Mystic
from enemies.act2.shelled_parasite import ShelledParasite
from enemies.act2.snake_plant import SnakePlant
from enemies.act2.snecko import Snecko
from enemies.act2.spheric_guardian import SphericGuardian
from enemies.act2.taskmaster import Taskmaster
from enemies.act2.the_champ import TheChamp
from enemies.act2.the_collector import TheCollector
from utils.types import EnemyType

class TestAct2Monsters(unittest.TestCase):
    def test_book_of_stabbing_hp(self):
        m = BookOfStabbing()
        self.assertGreaterEqual(m.hp, 40)

    def test_bronze_automaton_is_boss(self):
        m = BronzeAutomaton()
        self.assertEqual(m.enemy_type, EnemyType.BOSS)

    def test_bronze_automaton_sets_spawn_orbs_on_combat_start(self):
        m = BronzeAutomaton()
        m.on_combat_start(floor=1)
        self.assertIsNotNone(m.current_intention)
        self.assertEqual(m.current_intention.name, "Spawn Orbs")

    def test_bronze_orb_hp(self):
        m = BronzeOrb()
        self.assertGreaterEqual(m.hp, 20)

    def test_byrd_hp(self):
        m = Byrd()
        self.assertGreaterEqual(m.hp, 20)

    def test_centurion_hp(self):
        m = Centurion()
        self.assertGreaterEqual(m.hp, 50)

    def test_chosen_hp(self):
        m = Chosen()
        self.assertGreaterEqual(m.hp, 50)

    def test_gremlin_leader_is_elite(self):
        m = GremlinLeader()
        self.assertEqual(m.enemy_type, EnemyType.ELITE)

    def test_mugger_hp(self):
        m = Mugger()
        self.assertGreaterEqual(m.hp, 36)

    def test_mystic_hp(self):
        m = Mystic()
        self.assertGreaterEqual(m.hp, 36)

    def test_shelled_parasite_hp(self):
        m = ShelledParasite()
        self.assertGreaterEqual(m.hp, 62)

    def test_snake_plant_hp(self):
        m = SnakePlant()
        self.assertGreaterEqual(m.hp, 75)

    def test_snecko_hp(self):
        m = Snecko()
        self.assertGreaterEqual(m.hp, 50)

    def test_spheric_guardian_hp(self):
        m = SphericGuardian()
        self.assertGreaterEqual(m.hp, 55)

    def test_taskmaster_hp(self):
        m = Taskmaster()
        self.assertGreaterEqual(m.hp, 48)

    def test_the_champ_hp(self):
        m = TheChamp()
        self.assertGreaterEqual(m.hp, 100)

    def test_the_collector_is_elite(self):
        m = TheCollector()
        self.assertEqual(m.enemy_type, EnemyType.ELITE)

if __name__ == '__main__':
    unittest.main()
