from entities.creature import Creature
"""Comprehensive tests for Dual Wield card."""
import unittest
from utils.types import CardType, RarityType
from cards.ironclad.dual_wield import DualWield
from cards.ironclad.strike import Strike
from cards.ironclad.inflame import Inflame
from cards.ironclad.defend import Defend
from enemies.act1.cultist import Cultist
from tests.test_combat_utils import create_test_helper


class TestDualWield(unittest.TestCase):
    def setUp(self):
        self.helper = create_test_helper()

    def tearDown(self):
        self.helper._reset_game_state()

    def test_basic_properties(self):
        card = DualWield()
        self.assertEqual(card.cost, 1)
        self.assertEqual(card.card_type, CardType.SKILL)
        self.assertEqual(card.rarity, RarityType.UNCOMMON)
        self.assertEqual(card.upgrade_cost, 0)

    def test_energy_cost(self):
        player = self.helper.create_player(energy=3)
        enemy = self.helper.create_enemy(Cultist)
        self.helper.start_combat([enemy])
        
        card = DualWield()
        self.helper.add_card_to_hand(card)
        initial_energy = self.helper.game_state.player.energy
        self.helper.play_card(card, target=None)
        
        self.assertEqual(self.helper.game_state.player.energy, initial_energy - 1)

    def test_upgraded_cost(self):
        card = DualWield()
        card.upgrade()
        self.assertEqual(card.cost, 0)

    def test_can_only_copy_attack_or_power_cards(self):
        """Test that Dual Wield's ChooseCopyCardAction only includes Attack or Power cards."""
        # Import the action class
        from actions.card import ChooseCopyCardAction
        from utils.result_types import SingleActionResult
        from actions.display import SelectAction
        
        # Setup
        player = self.helper.create_player(energy=3)
        enemy = self.helper.create_enemy(Cultist)
        self.helper.start_combat([enemy])
        
        # Add different types of cards to hand
        attack_card = Strike()  # Attack card
        power_card = Inflame()  # Power card
        skill_card = Defend()   # Skill card
        
        self.helper.add_card_to_hand(attack_card)
        self.helper.add_card_to_hand(power_card)
        self.helper.add_card_to_hand(skill_card)
        
        # Create the action with the same parameters as Dual Wield uses
        action = ChooseCopyCardAction(
            pile="hand", 
            copies=1, 
            card_types=[CardType.ATTACK, CardType.POWER]
        )
        
        # Execute the action
        result = action.execute()
        
        # The action should return a SingleActionResult with a SelectAction
        self.assertIsInstance(result, SingleActionResult)
        self.assertIsInstance(result.action, SelectAction)
        
        # The SelectAction should have options only for Attack and Power cards (2 options)
        options = result.action.options
        self.assertEqual(len(options), 2, "Should only have options for Attack and Power cards, not Skill cards")
        
        # Verify that the options are for Attack and Power cards only
        for option in options:
            for act in option.actions:
                if hasattr(act, 'card'):
                    card = act.card
                    self.assertIn(card.card_type, [CardType.ATTACK, CardType.POWER],
                                 f"Card {card.__class__.__name__} should be Attack or Power, not {card.card_type}")
        
    def test_choose_copy_card_action_without_filter(self):
        """Test that ChooseCopyCardAction without card_types filter includes all cards."""
        # Import the action class
        from actions.card import ChooseCopyCardAction
        from utils.result_types import SingleActionResult
        from actions.display import SelectAction
        
        # Create a mock game state with different card types in hand
        player = self.helper.create_player(energy=3)
        enemy = self.helper.create_enemy(Cultist)
        self.helper.start_combat([enemy])
        
        # Add cards to hand
        attack_card = Strike()  # Attack card
        power_card = Inflame()  # Power card
        skill_card = Defend()   # Skill card
        
        self.helper.add_card_to_hand(attack_card)
        self.helper.add_card_to_hand(power_card)
        self.helper.add_card_to_hand(skill_card)
        
        # Create the action WITHOUT card_types filter (should include all cards)
        action = ChooseCopyCardAction(pile="hand", copies=1)
        
        # Execute the action
        result = action.execute()
        
        # The action should return a SingleActionResult with a SelectAction
        self.assertIsInstance(result, SingleActionResult)
        self.assertIsInstance(result.action, SelectAction)
        
        # Without filter, should have 3 options (all cards)
        options = result.action.options
        self.assertEqual(len(options), 3, "Without filter, should have all 3 cards as options")


if __name__ == '__main__':
    unittest.main()
