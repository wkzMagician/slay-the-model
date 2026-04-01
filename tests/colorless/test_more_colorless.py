from entities.creature import Creature
"""More colorless card tests"""
import unittest
from cards.colorless.apotheosis import Apotheosis
from cards.colorless.apparition import Apparition
from cards.colorless.blind import Blind
from cards.colorless.chrysalis import Chrysalis
from cards.colorless.dark_shackles import DarkShackles
from cards.colorless.dramatic_entrance import DramaticEntrance
from cards.colorless.enlightenment import Enlightenment
from cards.colorless.forethought import Forethought
from cards.colorless.good_instincts import GoodInstincts
from cards.colorless.impatience import Impatience
from cards.colorless.jax import JAX
from cards.colorless.master_of_strategy import MasterOfStrategy
from cards.colorless.mayhem import Mayhem
from cards.colorless.metamorphosis import Metamorphosis
from cards.colorless.panacea import Panacea
from cards.colorless.panache import Panache
from cards.colorless.panic_button import PanicButton
from cards.colorless.purify import Purify
from cards.colorless.sadistic_nature import SadisticNature
from cards.colorless.secret_technique import SecretTechnique
from cards.colorless.secret_weapon import SecretWeapon
from cards.colorless.swift_strike import SwiftStrike
from cards.colorless.the_bomb import TheBomb
from cards.colorless.thinking_ahead import ThinkingAhead
from cards.colorless.transmutation import Transmutation
from cards.colorless.trip import Trip
from cards.colorless.violence import Violence

class TestMoreColorless(unittest.TestCase):
    def test_apotheosis(self):
        card = Apotheosis()
        self.assertEqual(card.cost, 2)

    def test_apparition(self):
        card = Apparition()
        self.assertEqual(card.cost, 1)

    def test_blind(self):
        card = Blind()
        self.assertEqual(card.cost, 0)

    def test_chrysalis(self):
        card = Chrysalis()
        self.assertEqual(card.cost, 2)

    def test_dark_shackles(self):
        card = DarkShackles()
        self.assertEqual(card.cost, 0)

    def test_dramatic_entrance(self):
        card = DramaticEntrance()
        self.assertEqual(card.cost, 0)

    def test_enlightenment(self):
        card = Enlightenment()
        self.assertEqual(card.cost, 0)

    def test_forethought(self):
        card = Forethought()
        self.assertEqual(card.cost, 0)

    def test_good_instincts(self):
        card = GoodInstincts()
        self.assertEqual(card.cost, 0)

    def test_impatience(self):
        card = Impatience()
        self.assertEqual(card.cost, 0)

    def test_jax(self):
        card = JAX()
        self.assertEqual(card.cost, 0)

    def test_master_of_strategy(self):
        card = MasterOfStrategy()
        self.assertEqual(card.cost, 0)

    def test_mayhem(self):
        card = Mayhem()
        self.assertEqual(card.cost, 2)

    def test_metamorphosis(self):
        card = Metamorphosis()
        self.assertEqual(card.cost, 2)

    def test_panacea(self):
        card = Panacea()
        self.assertEqual(card.cost, 0)

    def test_panache(self):
        card = Panache()
        self.assertEqual(card.cost, 0)

    def test_panic_button(self):
        card = PanicButton()
        self.assertEqual(card.cost, 0)

    def test_panic_button_info_renders_turns(self):
        card = PanicButton()
        info = str(card.info())
        self.assertIn("2", info)

    def test_purify(self):
        card = Purify()
        self.assertEqual(card.cost, 0)

    def test_sadistic_nature(self):
        card = SadisticNature()
        self.assertEqual(card.cost, 0)
        self.assertIn("5", str(card.info()))
        card.upgrade()
        self.assertIn("7", str(card.info()))

    def test_secret_technique(self):
        card = SecretTechnique()
        self.assertEqual(card.cost, 0)

    def test_secret_weapon(self):
        card = SecretWeapon()
        self.assertEqual(card.cost, 0)

    def test_swift_strike(self):
        card = SwiftStrike()
        self.assertEqual(card.cost, 0)

    def test_the_bomb(self):
        card = TheBomb()
        self.assertEqual(card.cost, 2)

    def test_thinking_ahead(self):
        card = ThinkingAhead()
        self.assertEqual(card.cost, 0)

    def test_transmutation(self):
        card = Transmutation()
        self.assertEqual(card.cost, 3)

    def test_trip(self):
        card = Trip()
        self.assertEqual(card.cost, 0)

    def test_violence(self):
        card = Violence()
        self.assertEqual(card.cost, 0)

if __name__ == '__main__':
    unittest.main()
