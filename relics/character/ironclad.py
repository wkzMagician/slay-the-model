"""
Ironclad-specific relics - all Ironclad relics in one file.
"""
from engine.runtime_api import add_action, add_actions
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

    def on_combat_end(self):
        """Heal 6 HP at combat end"""
        from engine.game_state import game_state
        add_actions([HealAction(amount=6)])
        return
# Common Relic (Ironclad-specific)
@register("relic")
class RedSkull(Relic):
    """While your HP is at or below 50%, you have 3 additional Strength."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON
        self.strength_applied = False
        
    def on_combat_start(self, floor: int):
        self.strength_applied = False
        from engine.game_state import game_state
        player = game_state.player
        if player is None:
            return
        # Check if HP is already <= 50% at combat start
        if player.hp <= player.max_hp // 2:
            self.strength_applied = True
            add_actions([ApplyPowerAction(StrengthPower(amount=3, owner=player), player)])
            return
        return
    def on_any_hp_lost(self, amount, source=None, card=None):
        """Check if HP dropped to 50% or below"""
        from engine.game_state import game_state

        player = game_state.player
        if player is None:
            return
        if not self.strength_applied and amount > 0 and player.hp <= player.max_hp // 2:
            self.strength_applied = True
            add_actions([ApplyPowerAction(StrengthPower(amount=3, owner=player), player)])
            return
        return
    def on_heal(self, amount, source=None):
        """Check if HP went above 50% after heal, remove Strength if so"""
        from engine.game_state import game_state
        player = game_state.player
        if player is None:
            return
        if self.strength_applied:
            # Calculate HP after heal (before actual HP change)
            new_hp = min(player.hp + amount, player.max_hp)
            if new_hp > player.max_hp // 2:
                self.strength_applied = False
                add_actions([ApplyPowerAction(StrengthPower(amount=-3, owner=player), player)])
                return
        return
# PaperPhrog removed - duplicate of PaperPhrog in global_relics/uncommon.py

# Rare Relic
@register("relic")
class ChampionBelt(Relic):
    """Whenever you apply Vulnerable, also apply 1 Weak."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.RARE

    def on_apply_power(self, power, target):
        from powers.definitions.vulnerable import VulnerablePower
        from actions.combat import ApplyPowerAction
        
        if isinstance(power, VulnerablePower):
            from engine.game_state import game_state
            add_actions(
            [
                ApplyPowerAction(WeakPower(amount=1, owner=target), target)
            ]
            )
            return

        return
@register("relic")
class CharonsAshes(Relic):
    """Whenever you Exhaust a card, deal 3 damage to ALL enemies."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.RARE

    def on_card_exhausted(self, card, source_pile=None):
        from engine.game_state import game_state
        if game_state.player is None or not game_state.current_combat:
            return
        combat = game_state.current_combat
        add_actions(
        [
            DealDamageAction(damage=3, target=enemy)
            for enemy in list(combat.enemies)
            if not enemy.is_dead()
        ]
        )
        return

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

    def on_combat_end(self):
        """Heal 12 HP at combat end"""
        from engine.game_state import game_state
        add_actions([HealAction(amount=12)])
        return
@register("relic")
class RunicCube(Relic):
    """Whenever you lose HP, draw 1 card."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.BOSS

    def on_any_hp_lost(self, amount, source=None, card=None):
        if amount > 0:
            add_actions([DrawCardsAction(count=1)])
            return
        return


# Backward-compatible alias for existing imports/tests.
Runicube = RunicCube
# Shop Relic
@register("relic")
class Brimstone(Relic):
    """At the start of your turn, gain 2 Strength and ALL enemies gain 1 Strength."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.SHOP

    def on_player_turn_start(self):
        """Gain 2 Strength for player, 1 Strength for all enemies"""
        from engine.game_state import game_state
        player = game_state.player
        combat = game_state.current_combat
        if combat is None or player is None:
            return
        actions = [
            ApplyPowerAction(StrengthPower(amount=2, owner=player), player)
        ]
        for enemy in combat.enemies:
            if enemy.hp > 0:
                actions.append(ApplyPowerAction(StrengthPower(amount=1, owner=enemy), enemy))
        from engine.game_state import game_state
        add_actions(actions)
        return
@register("relic")
class OrangePellets(Relic):
    """Whenever you play a Power, Attack, and Skill in same turn, remove all of your Debuffs."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.SHOP
        self.power_count = 0
        self.attack_count = 0
        self.skill_count = 0
    
    def on_combat_start(self, floor: int):
        """Reset counters at start of combat"""
        add_actions([LambdaAction(func=lambda: self._reset_counters())])
        return
    def on_card_play(self, card, targets):
        """Track cards played and remove debuffs when all 3 types played"""
        from engine.game_state import game_state
        from utils.types import CardType
        from actions.combat import RemovePowerAction
        
        if card is None:
            return
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
            player = game_state.player
            if player is None:
                return
            for power in list(player.powers):
                if not power.is_buff:  # is a debuff
                    actions.append(RemovePowerAction(power=power.idstr, target=player, is_buff=False))
            
            self._reset_counters()
            add_actions(actions)
            return
        return
    def _reset_counters(self):
        self.power_count = 0
        self.attack_count = 0
        self.skill_count = 0
