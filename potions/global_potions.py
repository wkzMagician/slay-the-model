# Global Potions - Available to all characters
from typing import List
from actions.base import Action, LambdaAction
from actions.card import ChooseAddRandomCardAction, ChooseReplaceCardAction, DiscardCardAction, DrawCardsAction
from actions.combat import DealDamageAction, GainBlockAction, GainEnergyAction, ApplyPowerAction, HealAction
from actions.display import InputRequestAction
from actions.misc import EscapeAction
from actions.reward import AddRandomPotionAction
from potions.base import Potion
from utils.types import CardType, RarityType, TargetType
from utils.option import Option
from utils.random import get_random_card
from utils.registry import register
from localization import LocalStr

# Common Potions
@register("potion")
class AttackPotion(Potion):
    """From 3 random Attack cards, choose 1 to add to hand (cost 0)"""
    rarity = RarityType.COMMON
    category = "Global"
    name = "Attack Potion"

    def __init__(self):
        super().__init__()
        self._amount = 1  # Sacred Bark doubles to 2

    def on_use(self, targets) -> List[Action]:
        from utils.types import CardType
        actions = []
        for _ in range(self.amount):
            actions.append(ChooseAddRandomCardAction(
                pile='hand',
                total=1,
                card_type=CardType.ATTACK,
                temp_cost=0  # Set temporary cost to 0 for this turn
            ))
        return actions

@register("potion")
class BlockPotion(Potion):
    """Gain 12 Block (24 with Sacred Bark)"""
    rarity = RarityType.COMMON
    category = "Global"
    name = "Block Potion"

    def __init__(self):
        super().__init__()
        self._amount = 12  # Sacred Bark doubles to 24

    def on_use(self, targets) -> List[Action]:
        from engine.game_state import game_state
        return [GainBlockAction(block=self.amount, target=game_state.player)]

@register("potion")
class ColorlessPotion(Potion):
    """From 3 random Colorless cards, choose 1 to add to hand (cost 0)"""
    rarity = RarityType.COMMON
    category = "Global"
    name = "Colorless Potion"

    def __init__(self):
        super().__init__()
        self._amount = 1  # Sacred Bark doubles to 2

    def on_use(self, targets) -> List[Action]:
        from utils.types import CardType
        actions = []
        for _ in range(self.amount):
            actions.append(ChooseAddRandomCardAction(
                pile='hand',
                total=1,
                namespace="colorless",
                temp_cost=0  # Set temporary cost to 0 for this turn
            ))
        return actions

@register("potion")
class DexterityPotion(Potion):
    """Gain 2 Dexterity (4 with Sacred Bark)"""
    rarity = RarityType.COMMON
    category = "Global"
    name = "Dexterity Potion"

    def __init__(self):
        super().__init__()
        self._amount = 2  # Sacred Bark doubles to 4

    def on_use(self, targets) -> List[Action]:
        from engine.game_state import game_state
        return [ApplyPowerAction(power="Dexterity", target=game_state.player, amount=self.amount)]

@register("potion")
class EnergyPotion(Potion):
    """Gain 2 Energy (4 with Sacred Bark)"""
    rarity = RarityType.COMMON
    category = "Global"
    name = "Energy Potion"

    def __init__(self):
        super().__init__()
        self._amount = 2  # Sacred Bark doubles to 4

    def on_use(self, targets) -> List[Action]:
        return [GainEnergyAction(energy=self.amount)]

@register("potion")
class ExplosivePotion(Potion):
    """Deal 10 damage to all enemies (20 with Sacred Bark)"""
    rarity = RarityType.COMMON
    category = "Global"
    name = "Explosive Potion"
    target_type = TargetType.ENEMY_ALL
    def __init__(self):
        super().__init__()
        self._amount = 10  # Sacred Bark doubles to 20

    def on_use(self, targets) -> List[Action]:
        actions = []
        # targets is already resolved as list of all enemies
        for enemy in targets:
            actions.append(DealDamageAction(damage=self.amount, target=enemy))
        return actions

@register("potion")
class FearPotion(Potion):
    """Apply 3 Vulnerable to target enemy (6 with Sacred Bark)"""
    rarity = RarityType.COMMON
    category = "Global"
    name = "Fear Potion"
    target_type = TargetType.ENEMY_SELECT
    def __init__(self):
        super().__init__()
        self._amount = 3  # Sacred Bark doubles to 6

    def on_use(self, targets) -> List[Action]:
        # Apply Vulnerable to single target enemy
        return [ApplyPowerAction(power="Vulnerable", target=targets[0], amount=self.amount, duration=self.amount)]

@register("potion")
class FirePotion(Potion):
    """Deal 20 damage to target enemy (40 with Sacred Bark)"""
    rarity = RarityType.COMMON
    category = "Global"
    name = "Fire Potion"
    target_type = TargetType.ENEMY_SELECT
    def __init__(self):
        super().__init__()
        self._amount = 20  # Sacred Bark doubles to 40

    def on_use(self, targets) -> List[Action]:
        return [DealDamageAction(damage=self.amount, target=targets[0])]

@register("potion")
class FlexPotion(Potion):
    """Gain 5 Strength, lose equal amount at end of turn (10 with Sacred Bark)"""
    rarity = RarityType.COMMON
    category = "Global"
    name = "Flex Potion"

    def __init__(self):
        super().__init__()
        self._amount = 5  # Sacred Bark doubles to 10

    def on_use(self, targets) -> List[Action]:
        from engine.game_state import game_state
        # Apply Strength power
        actions = [
            ApplyPowerAction(power="Strength", target=game_state.player, amount=self.amount),
            ApplyPowerAction(power="StrengthDown", target=game_state.player, amount=self.amount, duration=1)  # This power should handle the strength loss at end of turn
        ]
        return actions

@register("potion")
class PowerPotion(Potion):
    """From 3 random Power cards, choose 1 to add to hand (cost 0)"""
    rarity = RarityType.COMMON
    category = "Global"
    name = "Power Potion"

    def __init__(self):
        super().__init__()
        self._amount = 1  # Sacred Bark doubles to 2

    def on_use(self, targets) -> List[Action]:
        from utils.types import CardType
        actions = []
        for _ in range(self.amount):
            actions.append(ChooseAddRandomCardAction(
                pile='hand',
                total=1,
                card_type=CardType.POWER,
                temp_cost=0  # Set temporary cost to 0 for this turn
            ))
        return actions

@register("potion")
class SkillPotion(Potion):
    """From 3 random Skill cards, choose 1 to add to hand (cost 0)"""
    rarity = RarityType.COMMON
    category = "Global"
    name = "Skill Potion"

    def __init__(self):
        super().__init__()
        self._amount = 1  # Sacred Bark doubles to 2

    def on_use(self, targets) -> List[Action]:
        from utils.types import CardType
        actions = []
        for _ in range(self.amount):
            actions.append(ChooseAddRandomCardAction(
                pile='hand',
                total=1,
                card_type=CardType.SKILL,
                temp_cost=0  # Set temporary cost to 0 for this turn
            ))
        return actions

@register("potion")
class SpeedPotion(Potion):
    """Gain 5 Dexterity, lose equal amount at end of turn (10 with Sacred Bark)"""
    rarity = RarityType.COMMON
    category = "Global"
    name = "Speed Potion"

    def __init__(self):
        super().__init__()
        self._amount = 5  # Sacred Bark doubles to 10

    def on_use(self, targets) -> List[Action]:
        from engine.game_state import game_state
        # Apply Dexterity power
        actions = [
            ApplyPowerAction(power="Dexterity", target=game_state.player, amount=self.amount),
            ApplyPowerAction(power="DexterityDown", target=game_state.player, amount=self.amount, duration=1)  # This power should handle the dexterity loss at end of turn
        ]
        return actions

@register("potion")
class StrengthPotion(Potion):
    """Gain 2 Strength (4 with Sacred Bark)"""
    rarity = RarityType.COMMON
    category = "Global"
    name = "Strength Potion"

    def __init__(self):
        super().__init__()
        self._amount = 2  # Sacred Bark doubles to 4

    def on_use(self, targets) -> List[Action]:
        from engine.game_state import game_state
        return [ApplyPowerAction(power="Strength", target=game_state.player, amount=self.amount)]

@register("potion")
class SwiftPotion(Potion):
    """Draw 3 cards (6 with Sacred Bark)"""
    rarity = RarityType.COMMON
    category = "Global"
    name = "Swift Potion"

    def __init__(self):
        super().__init__()
        self._amount = 3  # Sacred Bark doubles to 6

    def on_use(self, targets) -> List[Action]:
        return [DrawCardsAction(count=self.amount)]

@register("potion")
class WeakPotion(Potion):
    """Apply 3 Weak to target enemy (6 with Sacred Bark)"""
    rarity = RarityType.COMMON
    category = "Global"
    name = "Weak Potion"
    target_type = TargetType.ENEMY_SELECT
    def __init__(self):
        super().__init__()
        self._amount = 3  # Sacred Bark doubles to 6

    def on_use(self, targets) -> List[Action]:
        # Apply Weak to single target enemy
        return [ApplyPowerAction(power="Weak", target=targets[0], amount=self.amount, duration=self.amount)]

# Uncommon Potions
@register("potion")
class AncientPotion(Potion):
    """Gain 1 Artifact (2 with Sacred Bark)"""
    rarity = RarityType.UNCOMMON
    category = "Global"
    name = "Ancient Potion"

    def __init__(self):
        super().__init__()
        self._amount = 1  # Sacred Bark doubles to 2

    def on_use(self, targets) -> List[Action]:
        from engine.game_state import game_state
        return [ApplyPowerAction(power="Artifact", target=game_state.player, amount=self.amount)]

@register("potion")
class BlessingOfTheForge(Potion):
    """Upgrade all cards in hand for this battle"""
    rarity = RarityType.UNCOMMON
    category = "Global"
    name = "Blessing of the Forge"

    def __init__(self):
        super().__init__()

    def on_use(self, targets) -> List[Action]:
        from actions.card import UpgradeCardAction
        from engine.game_state import game_state
        
        # Upgrade all cards in hand
        actions = []
        for card in list(game_state.player.card_manager.get_pile("hand")):
            if card.can_upgrade():
                actions.append(UpgradeCardAction(card=card))
        
        return actions

@register("potion")
class DistilledChaos(Potion):
    """Auto-play top 3 cards from draw pile (6 with Sacred Bark)"""
    rarity = RarityType.UNCOMMON
    category = "Global"
    name = "Distilled Chaos"

    def __init__(self):
        super().__init__()
        self._amount = 3  # Sacred Bark doubles to 6

    def on_use(self, targets) -> List[Action]:
        from actions.combat import PlayCardAction
        from actions.card import RemoveCardAction, AddCardAction
        from engine.game_state import game_state
        
        actions = []
        draw_pile = game_state.player.card_manager.get_pile("draw")
        
        # Play top cards from draw pile
        for _ in range(min(self.amount, len(draw_pile))):
            if draw_pile:
                card = draw_pile.pop()
                # Play card automatically
                actions.extend([
                    PlayCardAction(card=card, is_auto=True, ignore_energy=True)
                ])
        
        return actions

@register("potion")
class DuplicationPotion(Potion):
    """Next card played twice (next 2 cards with Sacred Bark)"""
    rarity = RarityType.UNCOMMON
    category = "Global"
    name = "Duplication Potion"

    def __init__(self):
        super().__init__()
        self._amount = 1  # Sacred Bark doubles to 2 (number of cards to duplicate)

    def on_use(self, targets) -> List[Action]:
        # this is a power
        from engine.game_state import game_state
        return [ApplyPowerAction(power="Duplication", target=game_state.player, amount=self.amount)]

@register("potion")
class EssenceOfSteel(Potion):
    """Gain 4 Plated Armor (8 with Sacred Bark)"""
    rarity = RarityType.UNCOMMON
    category = "Global"
    name = "Essence of Steel"

    def __init__(self):
        super().__init__()
        self._amount = 4  # Sacred Bark doubles to 8

    def on_use(self, targets) -> List[Action]:
        from engine.game_state import game_state
        return [ApplyPowerAction(power="PlatedArmor", target=game_state.player, amount=self.amount)]

@register("potion")
class GamblersBrew(Potion):
    """Discard any cards from hand, then draw equal amount"""
    rarity = RarityType.UNCOMMON
    category = "Global"
    name = "Gambler's Brew"

    def __init__(self):
        super().__init__()

    def on_use(self, targets) -> List[Action]:
        return [ChooseReplaceCardAction(must_select=False)]

@register("potion")
class LiquidBronze(Potion):
    """Gain 3 Thorns (6 with Sacred Bark)"""
    rarity = RarityType.UNCOMMON
    category = "Global"
    name = "Liquid Bronze"

    def __init__(self):
        super().__init__()
        self._amount = 3  # Sacred Bark doubles to 6

    def on_use(self, targets) -> List[Action]:
        from engine.game_state import game_state
        return [ApplyPowerAction(power="Thorns", target=game_state.player, amount=self.amount)]

@register("potion")
class LiquidMemories(Potion):
    """Choose 1 card from discard to hand (2 with Sacred Bark, cost 0)"""
    rarity = RarityType.UNCOMMON
    category = "Global"
    name = "Liquid Memories"

    def __init__(self):
        super().__init__()
        self._amount = 1  # Sacred Bark doubles to 2

    def on_use(self, targets) -> List[Action]:
        from actions.card import AddCardAction
        from actions.card import RemoveCardAction
        from actions.display import InputRequestAction
        from engine.game_state import game_state
        from localization import LocalStr
        
        # Build options for each card in discard pile
        discard_pile = game_state.player.card_manager.get_pile("discard")
        options = []
        for card in discard_pile:
            options.append(Option(
                name=card.display_name,
                actions=[AddCardAction(card=card, dest_pile='hand')]
            ))
        
        # Add a "Done" option
        options.append(Option(
            name=LocalStr("ui.done"),
            actions=[]
        ))
        
        # Let player choose which card to return to hand
        return [InputRequestAction(title="Liquid Memories", options=options)]

@register("potion")
class RegenPotion(Potion):
    """Gain 5 Regeneration (10 with Sacred Bark)"""
    rarity = RarityType.UNCOMMON
    category = "Global"
    name = "Regen Potion"

    def __init__(self):
        super().__init__()
        self._amount = 5  # Sacred Bark doubles to 10

    def on_use(self, targets) -> List[Action]:
        from engine.game_state import game_state
        return [ApplyPowerAction(power="Regeneration", target=game_state.player, amount=self.amount)]

@register("potion")
class SmokeBomb(Potion):
    """Escape non-boss combat without rewards"""
    rarity = RarityType.UNCOMMON
    category = "Global"
    name = "Smoke Bomb"

    def __init__(self):
        super().__init__()

    def on_use(self, targets) -> List[Action]:
        from engine.game_state import game_state
        # Cannot use Smoke Bomb while Surrounded (Spire Shield + Spear elite)
        if game_state.player and game_state.player.has_power("Surrounded"):
            return []  # Blocked by Surrounded
        return [EscapeAction()]

# Rare Potions
@register("potion")
class FairyInABottle(Potion):
    """Heal 30% max HP when should die (60% with Sacred Bark) - Rare"""
    rarity = RarityType.RARE
    category = "Global"
    name = "Fairy in a Bottle"
    can_be_used_actively = False  # Only triggers on death

    def __init__(self):
        super().__init__()
        self._amount = 30  # Sacred Bark doubles to 60 (percentage)

    def on_use(self, targets) -> List[Action]:
        return [HealAction(target=targets[0], amount=int(targets[0].max_hp * (self.amount / 100.0)))]

@register("potion")
class FruitJuice(Potion):
    """Permanently gain 5 max HP (10 with Sacred Bark) - Rare"""
    rarity = RarityType.RARE
    category = "Global"
    name = "Fruit Juice"

    def __init__(self):
        super().__init__()
        self._amount = 5  # Sacred Bark doubles to 10

    def on_use(self, targets) -> List[Action]:
        from actions.combat import ModifyMaxHpAction
        return [ModifyMaxHpAction(amount=self.amount)]

@register("potion")
class SneckoOil(Potion):
    """Draw 5 cards (10 with Sacred Bark), randomize costs of cards in hand"""
    rarity = RarityType.RARE
    category = "Global"
    name = "Snecko Oil"

    def __init__(self):
        super().__init__()
        self._amount = 5  # Sacred Bark doubles to 10

    def on_use(self, targets) -> List[Action]:
        from actions.card import DrawCardsAction
        from engine.game_state import game_state
        
        # Draw cards
        actions = [
            DrawCardsAction(count=self.amount),
            LambdaAction(func=lambda: self.randomize_costs(game_state))
        ]
        return actions
    
    def randomize_costs(self, game_state):
        import random as rd
        # Randomize costs of cards in hand (including newly drawn cards)
        for card in game_state.player.card_manager.get_pile("hand"):
            # random: [0, 3]
            card.cost = rd.randint(0, 3)

@register("potion")
class CultistPotion(Potion):
    """Gain 1 Ritual (2 with Sacred Bark) - Rare"""
    rarity = RarityType.RARE
    category = "Global"
    name = "Cultist Potion"

    def __init__(self):
        super().__init__()
        self._amount = 1  # Sacred Bark doubles to 2

    def on_use(self, targets) -> List[Action]:
        from engine.game_state import game_state
        return [ApplyPowerAction(power="Ritual", target=game_state.player, amount=self.amount, duration=-1)]

@register("potion")
class EntropicBrew(Potion):
    """Fill all empty potion slots with random potions"""
    rarity = RarityType.RARE
    category = "Global"
    name = "Entropic Brew"

    def __init__(self):
        super().__init__()

    def on_use(self, targets) -> List[Action]:
        from engine.game_state import game_state
        
        actions = []
        
        # reuse AddRandomPotionAction for each empty slot
        for _ in range(game_state.player.potions.limit - len(game_state.player.potions)):
            actions.append(AddRandomPotionAction(game_state.player.character))
            
        return actions