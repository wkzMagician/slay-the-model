"""
Ironclad-specific relics - all Ironclad relics in one file.
"""
from typing import List
from actions.base import Action, LambdaAction
from actions.card import DrawCardsAction
from actions.combat import GainBlockAction, GainEnergyAction, HealAction, DealDamageAction, ApplyPowerAction
from powers.definitions.strength import StrengthPower
from powers.definitions.weak import WeakPower
# GainGoldAction imported lazily when needed to avoid circular import
from relics.base import Relic
from utils.types import RarityType, CardType
from utils.registry import register

# Common Relic - Ironclad starting relic
@register("relic")
class BurningBlood(Relic):
    """Ironclad starting relic: At end of combat, heal 6 HP."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON

    def on_combat_end(self, player, entities):
        """Heal 6 HP at combat end"""
        return [HealAction(amount=6)]

# Common Relic (Ironclad-specific)
@register("relic")
class RedSkull(Relic):
    """While your HP is at or below 50%, you have 3 additional Strength."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON
        self.strength_applied = False
        
    def on_combat_start(self, player, entities) -> List[Action]:
        self.strength_applied = False
        # Check if HP is already <= 50% at combat start
        if player.hp <= player.max_hp // 2:
            self.strength_applied = True
            return [ApplyPowerAction(StrengthPower(amount=3, owner=player), player)]
        return []
    
    def on_damage_taken(self, damage, source, player, entities) -> List[Action]:
        """Check if HP dropped to 50% or below"""
        if not self.strength_applied and player.hp <= player.max_hp // 2:
            self.strength_applied = True
            return [ApplyPowerAction(StrengthPower(amount=3, owner=player), player)]
        return []
    
    def on_heal(self, heal_amount, player, entities) -> List[Action]:
        """Check if HP went above 50% after heal, remove Strength if so"""
        if self.strength_applied:
            # Calculate HP after heal (before actual HP change)
            new_hp = min(player.hp + heal_amount, player.max_hp)
            if new_hp > player.max_hp // 2:
                self.strength_applied = False
                return [ApplyPowerAction(StrengthPower(amount=-3, owner=player), player)]
        return []
        

# PaperPhrog removed - duplicate of PaperPhrog in global_relics/uncommon.py

# Rare Relic
@register("relic")
class ChampionBelt(Relic):
    """Whenever you apply Vulnerable, also apply 1 Weak."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.RARE

    def on_apply_power(self, power, target, player, entities):
        from powers.definitions.vulnerable import VulnerablePower
        from actions.combat import ApplyPowerAction
        
        if isinstance(power, VulnerablePower):
            return [
                ApplyPowerAction(WeakPower(amount=1, owner=target), target)
            ]

        return []

@register("relic")
class CharonsAshes(Relic):
    """Whenever you Exhaust a card, deal 3 damage to ALL enemies."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.RARE

    def on_card_exhaust(self, card, player, entities):
        """When a card is exhausted, deal 3 damage to all enemies"""
        from engine.game_state import game_state
        actions = []
        assert game_state.current_combat is not None
        for enemy in game_state.current_combat.enemies:
            if enemy.hp > 0:
                actions.append(DealDamageAction(damage=3, target=enemy))
        return actions

@register("relic")
class MagicFlower(Relic):
    """Healing is 50% more effective during combat."""

    def __init__(self):
        super().__init__()
        self.rarity = RarityType.RARE

    def modify_heal(self, base_heal: int) -> int:
        """Increase healing by 50%."""
        if base_heal > 0:
            return int(base_heal * 1.5)
        return base_heal

# Boss Relic
@register("relic")
class BlackBlood(Relic):
    """Replaces Burning Blood. At the end of combat, heal 12 HP."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.BOSS

    def on_combat_end(self, player, entities):
        """Heal 12 HP at combat end"""
        return [HealAction(amount=12)]

@register("relic")
class Runicube(Relic):
    """Whenever you lose HP, draw 1 card."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.BOSS

    def on_damage_taken(self, damage, source, player, entities):
        """Draw 1 card when taking damage"""
        if damage > 0:
            return [DrawCardsAction(count=1)]
        return []

# Shop Relic
@register("relic")
class BrimStone(Relic):
    """At the start of your turn, gain 2 Strength and ALL enemies gain 1 Strength."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.SHOP

    def on_player_turn_start(self, player, entities):
        """Gain 2 Strength for player, 1 Strength for all enemies"""
        from engine.game_state import game_state
        actions = [
            ApplyPowerAction(StrengthPower(amount=2, owner=player), player)
        ]
        assert game_state.current_combat is not None
        for enemy in game_state.current_combat.enemies:
            if enemy.hp > 0:
                actions.append(ApplyPowerAction(StrengthPower(amount=1, owner=enemy), enemy))
        return actions

@register("relic")
class OrangePellets(Relic):
    """Whenever you play a Power, Attack, and Skill in same turn, remove all of your Debuffs."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.SHOP
        self.power_count = 0
        self.attack_count = 0
        self.skill_count = 0
    
    def on_combat_start(self, player, entities) -> List[Action]:
        """Reset counters at start of combat"""
        return [LambdaAction(func=lambda: self._reset_counters())]
    
    def on_card_play(self, card, player, entities):
        """Track cards played and remove debuffs when all 3 types played"""
        from utils.types import CardType
        from actions.combat import RemovePowerAction
        
        if card is None:
            return []
        if card.card_type == CardType.POWER:
            self.power_count += 1
        elif card.card_type == CardType.ATTACK:
            self.attack_count += 1
        elif card.card_type == CardType.SKILL:
            self.skill_count += 1
        
        # Check if all 3 types have been played this turn
        if (self.power_count > 0 and 
            self.attack_count > 0 and 
            self.skill_count > 0):
            # Remove all debuffs from player
            actions = []
            for power in list(player.powers):
                if not power.is_buff:  # is a debuff
                    actions.append(RemovePowerAction(power=power.idstr, target=player, is_buff=False))
            
            self._reset_counters()
            return actions
        return []

    def _reset_counters(self):
        self.power_count = 0
        self.attack_count = 0
        self.skill_count = 0
