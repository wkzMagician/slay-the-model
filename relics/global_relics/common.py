"""
Common Global Relics
Global relics available to all characters at common rarity.
"""
from typing import List
from actions.base import Action, LambdaAction
from actions.card import DrawCardsAction, AddCardAction
from actions.combat import GainBlockAction, GainEnergyAction, HealAction, DealDamageAction, ApplyPowerAction, ModifyMaxHpAction
# GainGoldAction imported lazily when needed to avoid circular import
from relics.base import Relic
from utils.types import RarityType, CardType
from utils.registry import register

# Already implemented relics
@register("relic")
class Akabeko(Relic):
    """Your first Attack each combat deals 8 additional damage"""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON
        
        # Track if first attack has been played this combat
        self.first_attack_played = False
    
    def on_combat_start(self, player, entities) -> List[Action]:
        """Reset first attack tracker at start of combat"""
        return [LambdaAction(func=lambda: setattr(self, 'first_attack_played', False))]

@register("relic")
class Anchor(Relic):
    """Gain 10 Block at start of first turn of each combat"""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON
    
    def on_player_turn_start(self, player, entities) -> List[Action]:
        # 第一回合，获得10点格挡
        from engine.game_state import game_state
        if (game_state.current_combat is not None and 
            game_state.current_combat.combat_state.combat_turn == 1):
            return [GainBlockAction(block=10, target=player)]
        return []

@register("relic")
class AncientTeaSet(Relic):
    """If last room is rest, gain 2 energy on_combat_start"""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON
        self.is_rest_last_room = False
        
    def on_player_turn_start(self, player, entities) -> List[Action]:
        """Gain 1 Energy on first turn"""
        if self.is_rest_last_room:
            self.is_rest_last_room = False  # Reset flag after use
            return [GainEnergyAction(energy=2)]
        return []

@register("relic")
class BagOfPreparation(Relic):
    """At the start of each combat, draw 2 additional cards."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON
    
    def on_combat_start(self, player, entities) -> List[Action]:
        """Draw 2 additional cards at the start of combat"""
        return [DrawCardsAction(count=2)]

@register("relic")
class Vajra(Relic):
    """Gain 1 Strength at start of combat"""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON
    
    def on_combat_start(self, player, entities) -> List[Action]:
        """Gain 1 Strength at start of combat"""
        return [ApplyPowerAction(power="Strength", target=player, amount=1)]

# New relics to implement
@register("relic")
class ArtOfWar(Relic):
    """If you do not play any Attacks during your turn, gain 1 extra Energy next turn"""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON
        self.attack_played_this_turn = False
        self.extra_energy_next_turn = False
    
    def on_player_turn_start(self, player, entities) -> List[Action]:
        """Grant extra energy if no attacks were played last turn"""
        self.attack_played_this_turn = False
        actions = []
        if self.extra_energy_next_turn:
            self.extra_energy_next_turn = False
            actions.append(GainEnergyAction(energy=1))
        self._reset_trackers()
        return actions
    
    def on_card_play(self, card, player, entities) -> List[Action]:
        """Track if an attack was played"""
        from utils.types import CardType
        if card.card_type == CardType.ATTACK:
            self.attack_played_this_turn = True
        return []
    
    def on_player_turn_end(self, player, entities) -> List[Action]:
        """Check if no attacks were played this turn"""
        if not self.attack_played_this_turn:
            self.extra_energy_next_turn = True
        return []
    
    def _reset_trackers(self):
        """Reset all trackers"""
        self.attack_played_this_turn = False
        self.extra_energy_next_turn = False

@register("relic")
class BagOfMarbles(Relic):
    """At the start of each combat, apply 1 Vulnerable to ALL enemies."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON
    
    def on_combat_start(self, player, entities) -> List[Action]:
        """Apply Vulnerable to all enemies at start of combat"""
        actions = []
        for enemy in entities:
            actions.append(ApplyPowerAction(power="Vulnerable", target=enemy, amount=1))
        return actions

@register("relic")
class BloodVial(Relic):
    """At the start of each combat, heal 2 HP."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON
    
    def on_combat_start(self, player, entities) -> List[Action]:
        """Heal 2 HP at start of combat"""
        return [HealAction(amount=2)]

@register("relic")
class BronzeScales(Relic):
    """Start each combat with 3 Thorns."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON
    
    def on_combat_start(self, player, entities) -> List[Action]:
        """Gain 3 Thorns at start of combat"""
        return [ApplyPowerAction(power="Thorns", target=player, amount=3)]

@register("relic")
class CentennialPuzzle(Relic):
    """The first time you lose HP each combat, draw 3 cards."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON
        self.first_loss_occurred = False
    
    def on_combat_start(self, player, entities) -> List[Action]:
        """Reset tracker at start of combat"""
        return [LambdaAction(func=lambda: setattr(self, 'first_loss_occurred', False))]
    
    def on_damage_taken(self, damage, source, player, entities) -> List[Action]:
        """Draw 3 cards on first HP loss each combat"""
        if damage > 0 and not self.first_loss_occurred:
            self.first_loss_occurred = True
            return [DrawCardsAction(count=3)]
        return []

@register("relic")
class CeramicFish(Relic):
    """Whenever you add a Card to your deck, gain 9 gold."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON
    
    # This would need to hook into card addition events
    # For now, implemented as a passive effect description
    # Implement in AddCardAction(pile="deck")

@register("relic")
class DreamCatcher(Relic):
    """Whenever you rest, you may add a Card to your deck."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON
    
    # This would need to hook into rest events
    # For now, implemented as a passive effect description
    # Implement in RestRoom, If has this relic, append a ChooseAddCardAction(deck="hand") after HealAction

@register("relic")
class HappyFlower(Relic):
    """Every 3 turns, gain 1 Energy."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON
        self.turn_counter = 0
    
    # doesn't need to reset in a new combat
    
    def on_player_turn_end(self, player, entities) -> List[Action]:
        """Check if we've reached 3 turns"""
        self.turn_counter += 1
        if self.turn_counter % 3 == 0 and self.turn_counter > 0:
            self.turn_counter = 0
            return [GainEnergyAction(energy=1)]
        return []

@register("relic")
class JuzuBracelet(Relic):
    """Regular enemy combats are no longer encountered in Event rooms."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON
    
    # This would need to hook into room generation
    # For now, implemented as a passive effect description

@register("relic")
class Lantern(Relic):
    """Gain 1 Energy on the first turn of each combat."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON
    
    def on_player_turn_start(self, player, entities) -> List[Action]:
        """Gain 1 Energy on first turn"""
        from engine.game_state import game_state
        if (game_state.current_combat is not None and 
            game_state.current_combat.combat_state.combat_turn == 1):
            return [GainEnergyAction(energy=1)]
        return []

@register("relic")
class MawBank(Relic):
    """Whenever you climb a floor, gain 12 Gold. No longer works when you spend any Gold at Shop."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON
        self.still_working = True
    
    def on_combat_start(self, player, entities) -> List[Action]:
        """Reset working flag at start of combat (new floor)"""
        return [LambdaAction(func=lambda: setattr(self, 'still_working', False))]
    
    # This would need to hook into floor climbing events
    # Also need to detect when gold is spent at shop to disable

@register("relic")
class MealTicket(Relic):
    """Whenever you enter a Shop room, heal 15 HP."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON
    
    # This would need to hook into room entry events
    # For now, implemented as a passive effect description

@register("relic")
class Nunchaku(Relic):
    """Every time you play 10 Attacks, gain 1 Energy."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON
        self.attacks_played = 0
    
    def on_card_play(self, card, player, entities) -> List[Action]:
        """Track attacks played"""
        from utils.types import CardType
        if card.card_type == CardType.ATTACK:
            self.attacks_played += 1
            if self.attacks_played >= 10:
                self.attacks_played = 0
                return [GainEnergyAction(energy=1)]
        return []

@register("relic")
class OddlySmoothStone(Relic):
    """At the start of each combat, gain 1 Dexterity."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON
    
    def on_combat_start(self, player, entities) -> List[Action]:
        """Gain 1 Dexterity at start of combat"""
        return [ApplyPowerAction(power="Dexterity", target=player, amount=1)]

@register("relic")
class Omamori(Relic):
    """Negate next 2 Curses you obtain."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON
        self.curses_to_negate = 2
    
    # This would need to hook into curse acquisition events
    # For now, implemented as a passive effect description

@register("relic")
class Orichalcum(Relic):
    """If you end your turn without Block, gain 6 Block."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON
    
    def on_player_turn_end(self, player, entities) -> List[Action]:
        """Gain 6 Block if you ended turn without Block"""
        from engine.game_state import game_state
        if game_state.player and game_state.player.block == 0:
            return [GainBlockAction(block=6, target=player)]
        return []

@register("relic")
class PenNib(Relic):
    """Every 10th Attack you play deals double damage."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON
        self.attacks_played = 0
        self.double_damage_next_attack = False
    
    def on_combat_start(self, player, entities) -> List[Action]:
        """Reset tracker at start of combat"""
        self.attacks_played = 0
        return [LambdaAction(func=lambda: setattr(self, 'attacks_played', 0))]
    
    def on_card_play(self, card, player, entities):
        """Track attacks and apply double damage on 10th"""
        from utils.types import CardType
        if card.card_type == CardType.ATTACK:
            self.attacks_played += 1
            # Check if this is the 10th attack (10, 20, 30, etc.)
            if self.attacks_played % 10 == 0:
                # Apply PenNibPower to player for the next attack
                return [ApplyPowerAction(power="PenNibPower", target=player, amount=1, duration=1)]
        return []

@register("relic")
class PotionBelt(Relic):
    """Upon pick up, gain 2 Potion slots."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON
    
    def on_obtain(self) -> List[Action]:
        from engine.game_state import game_state
        player = game_state.player
        player.potions.trim_to_limit(player.potion_limit + 2)
        return []

@register("relic")
class PreservedInsect(Relic):
    """Enemies in Elite rooms have 25% less HP."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON
    
    # This would need to hook into enemy generation for elite rooms
    # For now, implemented as a passive effect description

@register("relic")
class RegalPillow(Relic):
    """Heal an additional 15 HP when you rest."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON
    
    # This would need to hook into rest events
    # For now, implemented as a passive effect description

@register("relic")
class SmilingMask(Relic):
    """The Merchant's Card removal service now always costs 50 Gold."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON
    
    # This would need to hook into shop/card removal events
    # For now, implemented as a passive effect description

@register("relic")
class Strawberry(Relic):
    """Obtain: Max HP + 7."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON
    
    def on_obtain(self) -> List[Action]:
        return [ModifyMaxHpAction(amount=7)]

@register("relic")
class TheBoot(Relic):
    """Whenever you would deal 4 or less unblocked Attack damage, increase it to 5."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON
    
    # This would need to hook into damage calculation
    # For now, implemented as a passive effect description
    # Implement in resolve_potential_damage

@register("relic")
class TinyChest(Relic):
    """Every 4th Event room is a Treasure room."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON
        self.event_count = 0
    
    # This would need to hook into room generation
    # For now, implemented as a passive effect description

@register("relic")
class ToyOrnithopter(Relic):
    """Whenever you drink a Potion, heal 5 HP."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON
    
    # todo: on_use_potion

@register("relic")
class WarPaint(Relic):
    """Upon pickup, upgrade 2 random Skills."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON
    
    def on_obtain(self) -> List[Action]:
        from actions.card import UpgradeRandomCardAction
        return [UpgradeRandomCardAction(card_type="Skill", count=2)]

@register("relic")
class Whetstone(Relic):
    """Upon pickup, upgrade 2 random Attacks."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON
    
    def on_obtain(self) -> List[Action]:
        from actions.card import UpgradeRandomCardAction
        return [UpgradeRandomCardAction(card_type="Attack", count=2)]
