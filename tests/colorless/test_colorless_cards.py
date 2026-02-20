"""Test colorless cards"""
import unittest
from cards.colorless.burn import Burn
from cards.colorless.dazed import Dazed
from cards.colorless.wound import Wound
from cards.colorless.injury import Injury
from cards.colorless.decay import Decay
from cards.colorless.clumsy import Clumsy
from cards.colorless.doubt import Doubt
from cards.colorless.finesse import Finesse
from cards.colorless.flash_of_steel import FlashOfSteel
from cards.colorless.bite import Bite
from cards.colorless.bandage_up import BandageUp
from cards.colorless.hand_of_greed import HandOfGreed
from cards.colorless.deep_breath import DeepBreath
from cards.colorless.discovery import Discovery
from cards.colorless.madness import Madness
from cards.colorless.magnetism import Magnetism
from cards.colorless.jack_of_all_trades import JackOfAllTrades
from tests.test_combat_utils import CombatTestHelper

class TestStatusCards(unittest.TestCase):
    def test_burn_exists(self):
        card = Burn()

    def test_dazed_exists(self):
        card = Dazed()

    def test_wound_exists(self):
        card = Wound()

    def test_injury_exists(self):
        card = Injury()

    def test_decay_exists(self):
        card = Decay()

    def test_clumsy_exists(self):
        card = Clumsy()

    def test_doubt_exists(self):
        card = Doubt()

class TestSkillCards(unittest.TestCase):
    def test_finesse_properties(self):
        card = Finesse()
        self.assertEqual(card.cost, 0)

    def test_flash_of_steel_properties(self):
        card = FlashOfSteel()
        self.assertEqual(card.cost, 0)

    def test_bite_properties(self):
        card = Bite()
        self.assertEqual(card.cost, 1)

    def test_bandage_up_properties(self):
        card = BandageUp()
        self.assertEqual(card.cost, 0)

    def test_hand_of_greed_properties(self):
        card = HandOfGreed()
        self.assertEqual(card.cost, 2)

    def test_deep_breath_properties(self):
        card = DeepBreath()
        self.assertEqual(card.cost, 0)

    def test_discovery_properties(self):
        card = Discovery()
        self.assertEqual(card.cost, 1)

    def test_madness_properties(self):
        card = Madness()
        self.assertEqual(card.cost, 1)

    def test_magnetism_properties(self):
        card = Magnetism()
        self.assertEqual(card.cost, 2)

    def test_jack_of_all_trades_properties(self):
        card = JackOfAllTrades()
        self.assertEqual(card.cost, 0)

if __name__ == '__main__':
    unittest.main()
