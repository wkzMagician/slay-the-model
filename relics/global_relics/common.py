"""
Common Global Relics
Global relics available to all characters at common rarity.
"""
from engine.runtime_api import add_action, add_actions
from typing import List
from actions.base import Action, LambdaAction
from actions.card import DrawCardsAction, AddCardAction
from actions.combat import GainBlockAction, GainEnergyAction, HealAction, DealDamageAction, ApplyPowerAction, ModifyMaxHpAction
from powers.definitions.strength import StrengthPower
from powers.definitions.vulnerable import VulnerablePower
from powers.definitions.thorns import ThornsPower
from powers.definitions.dexterity import DexterityPower
from powers.definitions.pen_nib import PenNibPower
# GainGoldAction imported lazily when needed to avoid circular import
from relics.base import Relic
from utils.types import RarityType, CardType
from utils.registry import register

# Already implemented relics
from utils.damage_phase import DamagePhase

@register("relic")
class Akabeko(Relic):
    """Your first Attack each combat deals 8 additional damage"""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON
        self.damage_phase = DamagePhase.ADDITIVE  # +8 damage
        
        # Track if first attack has been played this combat
        self.first_attack_played = False
    
    def on_combat_start(self, player, entities):
        """Reset first attack tracker at start of combat"""
        self.first_attack_played = False
        return
    def on_card_play(self, card, player, targets):
        """Track when first attack is played"""
        if not self.first_attack_played and card.card_type == CardType.ATTACK:
            self.first_attack_played = True
        return
    def modify_damage_dealt(self, base_damage: int, card=None, target=None) -> int:
        """Add 8 damage to first attack each combat"""
        if not self.first_attack_played and card and card.card_type == CardType.ATTACK:
            return base_damage + 8
        return base_damage

@register("relic")
class Anchor(Relic):
    """Gain 10 Block at start of first turn of each combat"""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON
    
    def on_player_turn_start(self, player, entities):
        from engine.game_state import game_state
        if (game_state.current_combat is not None and 
            game_state.current_combat.combat_state.combat_turn == 1):
            from engine.game_state import game_state
            add_actions([GainBlockAction(block=10, target=player)])
            return
        return
@register("relic")
class AncientTeaSet(Relic):
    """If last room is rest, gain 2 energy on_combat_start"""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON
        self.is_rest_last_room = False
        
    def on_player_turn_start(self, player, entities):
        """Gain 1 Energy on first turn"""
        if self.is_rest_last_room:
            self.is_rest_last_room = False  # Reset flag after use
            from engine.game_state import game_state
            add_actions([GainEnergyAction(energy=2)])
            return
        return
@register("relic")
class BagOfPreparation(Relic):
    """At the start of each combat, draw 2 additional cards."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON
    
    def on_combat_start(self, player, entities):
        """Draw 2 additional cards at the start of combat"""
        from engine.game_state import game_state
        add_actions([DrawCardsAction(count=2)])
        return
@register("relic")
class Vajra(Relic):
    """Gain 1 Strength at start of combat"""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON
    
    def on_combat_start(self, player, entities):
        """Gain 1 Strength at start of combat"""
        from engine.game_state import game_state
        add_actions([ApplyPowerAction(StrengthPower(amount=1, owner=player), player)])
        return
# New relics to implement
@register("relic")
class ArtOfWar(Relic):
    """If you do not play any Attacks during your turn, gain 1 extra Energy next turn"""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON
        self.attack_played_this_turn = False
        self.extra_energy_next_turn = False
    
    def on_player_turn_start(self, player, entities):
        """Grant extra energy if no attacks were played last turn"""
        actions = []
        if self.extra_energy_next_turn:
            self.extra_energy_next_turn = False
            actions.append(GainEnergyAction(energy=1))
        # Reset attack tracker for this turn
        self.attack_played_this_turn = False
        from engine.game_state import game_state
        add_actions(actions)
        return
    def on_card_play(self, card, player, targets):
        """Track if an attack was played"""
        from utils.types import CardType
        if card.card_type == CardType.ATTACK:
            self.attack_played_this_turn = True
        return
    def on_player_turn_end(self, player, entities):
        """Check if no attacks were played this turn"""
        if not self.attack_played_this_turn:
            self.extra_energy_next_turn = True
        return
@register("relic")
class BagOfMarbles(Relic):
    """At the start of each combat, apply 1 Vulnerable to ALL enemies."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON
    
    def on_combat_start(self, player, entities):
        """Apply Vulnerable to all enemies at start of combat"""
        actions = []
        for enemy in entities:
            actions.append(ApplyPowerAction(VulnerablePower(amount=1, owner=enemy), enemy))

        from engine.game_state import game_state

        add_actions(actions)

        return
@register("relic")
class BloodVial(Relic):
    """At the start of each combat, heal 2 HP."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON
    
    def on_combat_start(self, player, entities):
        """Heal 2 HP at start of combat"""
        from engine.game_state import game_state
        add_actions([HealAction(amount=2)])
        return
@register("relic")
class BronzeScales(Relic):
    """Start each combat with 3 Thorns."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON
    
    def on_combat_start(self, player, entities):
        """Gain 3 Thorns at start of combat"""
        from engine.game_state import game_state
        add_actions([ApplyPowerAction(ThornsPower(amount=3, owner=player), player)])
        return
@register("relic")
class CentennialPuzzle(Relic):
    """The first time you lose HP each combat, draw 3 cards."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON
        self.first_loss_occurred = False
    
    def on_combat_start(self, player, entities):
        """Reset tracker at start of combat"""
        from engine.game_state import game_state
        add_actions([LambdaAction(func=lambda: setattr(self, 'first_loss_occurred', False))])
        return
    def on_damage_taken(self, damage, source, player, entities):
        """Draw 3 cards on first HP loss each combat"""
        if damage > 0 and not self.first_loss_occurred:
            self.first_loss_occurred = True
            from engine.game_state import game_state
            add_actions([DrawCardsAction(count=3)])
            return
        return
@register("relic")
class CeramicFish(Relic):
    """Whenever you add a Card to your deck, gain 9 gold."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON

    def on_card_added(self, card, dest_pile: str = "deck"):
        from actions.reward import AddGoldAction

        if dest_pile == "deck":
            from engine.game_state import game_state
            add_actions([AddGoldAction(amount=9)])
            return
        return
@register("relic")
class DreamCatcher(Relic):
    """Whenever you rest, you may add a Card to your deck."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON

@register("relic")
class HappyFlower(Relic):
    """Every 3 turns, gain 1 Energy."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON
        self.turn_counter = 0
    
    # doesn't need to reset in a new combat
    
    def on_player_turn_end(self, player, entities):
        """Check if we've reached 3 turns"""
        self.turn_counter += 1
        if self.turn_counter % 3 == 0 and self.turn_counter > 0:
            self.turn_counter = 0
            from engine.game_state import game_state
            add_actions([GainEnergyAction(energy=1)])
            return
        return
@register("relic")
class JuzuBracelet(Relic):
    """Regular enemy combats are no longer encountered in Event rooms."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON
    
    # This hook into room generation

@register("relic")
class Lantern(Relic):
    """Gain 1 Energy on the first turn of each combat."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON
    
    def on_player_turn_start(self, player, entities):
        """Gain 1 Energy on first turn"""
        from engine.game_state import game_state
        if (game_state.current_combat is not None and 
            game_state.current_combat.combat_state.combat_turn == 1):
            from engine.game_state import game_state
            add_actions([GainEnergyAction(energy=1)])
            return
        return
@register("relic")
class MawBank(Relic):
    """Whenever you climb a floor, gain 12 Gold. No longer works when you spend any Gold at Shop."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON
        self.still_working = True
        self._shop_spend_baseline = None
    
    def on_combat_start(self, player, entities):
        """Gain 12 Gold while active and disable after shop spending."""
        from engine.game_state import game_state
        from actions.reward import AddGoldAction

        current_spent = getattr(game_state, "gold_spent_in_shop", 0)
        if self._shop_spend_baseline is None:
            self._shop_spend_baseline = current_spent
        elif current_spent > self._shop_spend_baseline:
            self.still_working = False

        if not self.still_working:
            return
        from engine.game_state import game_state
        add_actions([AddGoldAction(amount=12)])
        return
@register("relic")
class MealTicket(Relic):
    """Whenever you enter a Shop room, heal 15 HP."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON

    def on_shop_enter(self, player, entities=None):
        """Heal 15 HP when entering a shop room."""
        from engine.game_state import game_state
        add_actions([HealAction(amount=15, target=player)])
        return
@register("relic")
class Nunchaku(Relic):
    """Every time you play 10 Attacks, gain 1 Energy."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON
        self.attacks_played = 0
    
    def on_card_play(self, card, player, targets):
        """Track attacks played"""
        from utils.types import CardType
        if card.card_type == CardType.ATTACK:
            self.attacks_played += 1
            if self.attacks_played >= 10:
                self.attacks_played = 0
                from engine.game_state import game_state
                add_actions([GainEnergyAction(energy=1)])
                return
        return
@register("relic")
class OddlySmoothStone(Relic):
    """At the start of each combat, gain 1 Dexterity."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON
    
    def on_combat_start(self, player, entities):
        """Gain 1 Dexterity at start of combat"""
        from engine.game_state import game_state
        add_actions([ApplyPowerAction(DexterityPower(amount=1, owner=player), player)])
        return
@register("relic")
class Omamori(Relic):
    """Negate next 2 Curses you obtain."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON
        self.curses_to_negate = 2

    def try_negate_curse(self) -> bool:
        """Consume one charge to negate a curse gain."""
        if self.curses_to_negate <= 0:
            return False
        self.curses_to_negate -= 1
        return True


@register("relic")
class Orichalcum(Relic):
    """If you end your turn without Block, gain 6 Block."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON
    
    def on_player_turn_end(self, player, entities):
        """Gain 6 Block if you ended turn without Block"""
        from engine.game_state import game_state
        if game_state.player and game_state.player.block == 0:
            from engine.game_state import game_state
            add_actions([GainBlockAction(block=6, target=player)])
            return
        return
@register("relic")
class PenNib(Relic):
    """Every 10th Attack you play deals double damage."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON
        self.attacks_played = 0
    
    def on_combat_start(self, player, entities):
        """Reset tracker at start of combat"""
        self.attacks_played = 0
        return
    def on_card_play(self, card, player, targets):
        """Track attacks and apply double damage on 10th"""
        from utils.types import CardType
        if card.card_type == CardType.ATTACK:
            self.attacks_played += 1
            # Check if this is the 10th attack (10, 20, 30, etc.)
            # The 10th attack itself deals double damage
            if self.attacks_played % 10 == 0:
                from engine.game_state import game_state
                add_actions([ApplyPowerAction(PenNibPower(amount=1, owner=player), player)])
                return
        return
@register("relic")
class PotionBelt(Relic):
    """Upon pick up, gain 2 Potion slots."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON
    
    def on_obtain(self):
        from engine.game_state import game_state
        player = game_state.player
        player.potions.trim_to_limit(player.potion_limit + 2)
        return
@register("relic")
class PreservedInsect(Relic):
    """Enemies in Elite rooms have 25% less HP."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON

    def apply_elite_hp_reduction(self, enemies) -> None:
        """Reduce elite enemies' max HP by 25% at combat setup."""
        for enemy in enemies:
            reduced_max_hp = max(1, int(enemy.max_hp * 0.75))
            enemy.max_hp = reduced_max_hp
            enemy.hp = min(enemy.hp, reduced_max_hp)
    
@register("relic")
class RegalPillow(Relic):
    """Heal an additional 15 HP when you rest."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON

    def modify_rest_heal(self, base_heal: int) -> int:
        """Increase heal amount while resting."""
        return base_heal + 15


@register("relic")
class SmilingMask(Relic):
    """The Merchant's Card removal service now always costs 50 Gold."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON
    
    # This hook into shop/card removal events

@register("relic")
class Strawberry(Relic):
    """Obtain: Max HP + 7."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON
    
    def on_obtain(self):
        from engine.game_state import game_state
        add_actions([ModifyMaxHpAction(amount=7)])
        return
@register("relic")
class TheBoot(Relic):
    """Whenever you deal 4 or less damage with an Attack, deal 5 instead."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON
        self.damage_phase = DamagePhase.CAPPING  # Minimum damage clamping
    
    def modify_damage_dealt(self, base_damage: int, card=None, target=None) -> int:
        """Increase damage to 5 if it's 4 or less from Attack cards."""
        if card and hasattr(card, 'card_type') and card.card_type == CardType.ATTACK:
            if base_damage <= 4:
                return 5
        return base_damage

@register("relic")
class TinyChest(Relic):
    """Every 4th Event room is a Treasure room."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON
        self.event_count = 0
    
    # This hook into room generation

@register("relic")
class ToyOrnithopter(Relic):
    """Whenever you drink a Potion, heal 5 HP."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON

    def on_use_potion(self, potion, player, entities):
        """Heal 5 HP whenever a potion is consumed."""
        from engine.game_state import game_state
        add_actions([HealAction(amount=5, target=player)])
        return
@register("relic")
class WarPaint(Relic):
    """Upon pickup, upgrade 2 random Skills."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON
    
    def on_obtain(self):
        from actions.card import UpgradeRandomCardAction
        from engine.game_state import game_state
        add_actions([UpgradeRandomCardAction(card_type="Skill", count=2)])
        return
@register("relic")
class Whetstone(Relic):
    """Upon pickup, upgrade 2 random Attacks."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON
    
    def on_obtain(self):
        from actions.card import UpgradeRandomCardAction
        from engine.game_state import game_state
        add_actions([UpgradeRandomCardAction(card_type="Attack", count=2)])
        return
