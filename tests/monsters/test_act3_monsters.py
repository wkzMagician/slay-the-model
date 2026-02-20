"""Test Act 3 monsters"""
import unittest
from enemies.act3.awakened_one import AwakenedOne
from enemies.act3.dagger import Dagger
from enemies.act3.darkling import Darkling
from enemies.act3.exploder import Exploder
from enemies.act3.giant_head import GiantHead
from enemies.act3.nemesis import Nemesis
from enemies.act3.orb_walker import OrbWalker
from enemies.act3.reptomancer import Reptomancer
from enemies.act3.repulsor import Repulsor
from enemies.act3.spiker import Spiker
from enemies.act3.spire_growth import SpireGrowth
from enemies.act3.time_eater import TimeEater
from enemies.act3.transient import Transient
from enemies.act3.writhing_mass import WrithingMass
from utils.types import EnemyType

class TestAct3Monsters(unittest.TestCase):
    def test_awakened_one_is_boss(self):
        m = AwakenedOne()
        self.assertEqual(m.enemy_type, EnemyType.BOSS)

    def test_dagger_hp(self):
        m = Dagger()
        self.assertGreaterEqual(m.hp, 10)

    def test_darkling_hp(self):
        m = Darkling()
        self.assertGreaterEqual(m.hp, 50)

    def test_exploder_hp(self):
        m = Exploder()
        self.assertGreaterEqual(m.hp, 20)

    def test_giant_head_is_elite(self):
        m = GiantHead()
        self.assertEqual(m.enemy_type, EnemyType.ELITE)

    def test_nemesis_is_elite(self):
        m = Nemesis()
        self.assertEqual(m.enemy_type, EnemyType.ELITE)

    def test_orb_walker_hp(self):
        m = OrbWalker()
        self.assertGreaterEqual(m.hp, 50)

    def test_reptomancer_hp(self):
        m = Reptomancer()
        self.assertGreaterEqual(m.hp, 100)

    def test_repulsor_hp(self):
        m = Repulsor()
        self.assertGreaterEqual(m.hp, 40)

    def test_spiker_hp(self):
        m = Spiker()
        self.assertGreaterEqual(m.hp, 40)

    def test_spire_growth_hp(self):
        m = SpireGrowth()
        self.assertGreaterEqual(m.hp, 100)

    def test_time_eater_is_boss(self):
        m = TimeEater()
        self.assertEqual(m.enemy_type, EnemyType.BOSS)

    def test_transient_hp(self):
        m = Transient()
        self.assertGreaterEqual(m.hp, 50)

    def test_writhing_mass_hp(self):
        m = WrithingMass()
        self.assertGreaterEqual(m.hp, 100)

if __name__ == '__main__':
    unittest.main()
