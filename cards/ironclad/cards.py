"""
Ironclad card package - all warrior class cards in one file
"""

from typing import List
from actions.base import Action
from actions.card import AddCardAction, ChooseUpgradeCardAction
from actions.combat import LoseHPAction, GainEnergyAction, ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import RarityType

# ==================== Starter Deck Cards ====================

@register("card")
class Strike(Card):
    """Deal damage"""
    
    # Card attributes
    card_type = "Attack"
    rarity = RarityType.STARTER
    
    # Card values
    base_cost = 1
    base_damage = 6
    base_attack_times = 1
    
    # Upgrade values
    upgrade_damage = 9


@register("card")
class Defend(Card):
    """Gain block"""
    
    # Card attributes
    card_type = "Skill"
    rarity = RarityType.STARTER
    
    # Card values
    base_cost = 1
    base_block = 5
    
    # Upgrade values
    upgrade_block = 8


@register("card")
class Bash(Card):
    """Deal damage and apply Vulnerable"""
    
    # Card attributes
    card_type = "Attack"
    rarity = RarityType.STARTER
    
    # Card values
    base_cost = 2
    base_damage = 8
    base_magic = {"vulnerable": 2}
    
    # Upgrade values
    upgrade_damage = 10
    upgrade_magic = {"vulnerable": 3}
    
    def on_play(self, target: Creature | None = None) -> List[Action]:
        # todo: ApplyPowerAction, apply vulnerable to target
        return super().on_play(target) + ApplyPowerAction(target=target, power="vulnerable", amount=self.get_temp_value("magic_vulnerable"))


@register("card")
class Anger(Card):
    """Deal damage and add a copy to discard pile"""
    
    # Card attributes
    card_type = "Attack"
    rarity = RarityType.STARTER
    
    # Card values
    base_cost = 0
    base_damage = 6
    base_draw = 0  # Will add copy to discard via magic
    
    # Upgrade values
    upgrade_damage = 8
    
    def on_play(self, target: Creature | None = None) -> List[Action]:
        # 复制一份自身，放入弃牌堆中
        return super().on_play(target) + [AddCardAction(card=self, dest_pile="discard")]


# ==================== Common Cards ====================

@register("card")
class IronWave(Card):
    """Gain block and deal damage"""
    
    # Card attributes
    card_type = "Attack"
    rarity = RarityType.COMMON
    
    # Card values
    base_cost = 1
    base_block = 5
    base_damage = 5
    
    # Upgrade values
    upgrade_block = 7
    upgrade_damage = 7


@register("card")
class PommelStrike(Card):
    """Deal damage and draw cards"""
    
    # Card attributes
    card_type = "Attack"
    rarity = RarityType.COMMON
    
    # Card values
    base_cost = 1
    base_damage = 9
    base_draw = 1
    
    # Upgrade values
    upgrade_damage = 10
    upgrade_draw = 2


# todo: 重刃独特的力量加成
@register("card")
class HeavyBlade(Card):
    """Deal damage, Strength affects this multiple times"""
    
    # Card attributes
    card_type = "Attack"
    rarity = RarityType.COMMON
    
    # Card values
    base_cost = 2
    base_damage = 14
    base_magic = {"strength_mult": 3}
    
    # Upgrade values
    upgrade_damage = 17
    upgrade_magic = {"strength_mult": 5}


@register("card")
class Armaments(Card):
    """Gain block and upgrade a card in hand"""
    
    # Card attributes
    card_type = "Skill"
    rarity = RarityType.COMMON
    
    # Card values
    base_cost = 1
    base_block = 5
    base_magic = {"upgrade_hand": 1}
    
    # Upgrade values
    upgrade_block = 7
    upgrade_magic = {"upgrade_hand": -1}
    
    def on_play(self, target: Creature | None = None) -> List[Action]:
        return super().on_play(target) + ChooseUpgradeCardAction(pile="hand", amount=self.get_temp_value("magic_upgrade_hand"))


@register("card")
class Flex(Card):
    """Gain Strength, lose it at end of turn"""
    
    # Card attributes
    card_type = "Power"
    rarity = RarityType.COMMON
    
    # Card values
    base_cost = 0
    base_magic = {"temp_strength": 2}
    
    # Upgrade values
    upgrade_magic = {"temp_strength": 4}
    
    def on_play(self, target: Creature | None = None) -> List[Action]:
        return super().on_play(target) + [ApplyPowerAction(target=target, power="flex", amount=self.get_temp_value("magic_temp_strength"))]


# ==================== Uncommon Cards ====================

@register("card")
class Clothesline(Card):
    """Deal damage and apply Weak"""
    
    # Card attributes
    card_type = "Attack"
    rarity = RarityType.UNCOMMON
    
    # Card values
    base_cost = 2
    base_damage = 12
    base_magic = {"weak": 2}
    
    # Upgrade values
    upgrade_damage = 14
    upgrade_magic = {"weak": 3}
    
    def on_play(self, target: Creature | None = None) -> List[Action]:
        return super().on_play(target) + ApplyPowerAction(target=target, power="weak", amount=self.get_temp_value("magic_weak"))


@register("card")
class Inflame(Card):
    """Gain Strength for this combat"""
    
    # Card attributes
    card_type = "Power"
    rarity = RarityType.UNCOMMON
    
    # Card values
    base_cost = 1
    base_magic = {"strength": 2}
    
    # Upgrade values
    upgrade_magic = {"strength": 3}
    
    def on_play(self, target: Creature | None = None) -> List[Action]:
        return super().on_play(target) + [ApplyPowerAction(target=target, power="strength", amount=self.get_temp_value("magic_strength"))]


@register("card")
class BodySlam(Card):
    """Deal damage equal to your block"""
    
    # Card attributes
    card_type = "Attack"
    rarity = RarityType.UNCOMMON
    
    # Card values
    base_cost = 1
    
    # Upgrade values
    upgrade_cost = 0
    
    # todo: 攻击力等于防御力的逻辑在哪里实现？


@register("card")
class Carnage(Card):
    """Deal massive damage to all enemies"""
    
    # Card attributes
    card_type = "Attack"
    rarity = RarityType.UNCOMMON
    
    # Card values
    base_cost = 2
    base_damage = 20
    base_ethereal = True
    
    # Upgrade values
    upgrade_damage = 28


# ==================== Rare Cards ====================

@register("card")
class Bludgeon(Card):
    """Deal massive damage"""
    
    # Card attributes
    card_type = "Attack"
    rarity = RarityType.RARE
    
    # Card values
    base_cost = 3
    base_damage = 32
    
    # Upgrade values
    upgrade_damage = 42


@register("card")
class LimitBreak(Card):
    """Double your Strength"""
    
    # Card attributes
    card_type = "Skill"
    rarity = RarityType.RARE
    
    # Card values
    base_cost = 1
    base_exhaust = True
    
    # Upgrade values
    upgrade_exhaust = False
    
    def on_play(self, target: Creature | None = None) -> List[Action]:
        from engine.game_state import game_state
        strength_power = game_state.player.get_power("strength")
        strength_amount = strength_power.amount if strength_power else 0
        return super().on_play(target) + [ApplyPowerAction(target=target, power="strength", amount=strength_amount)]


@register("card")
class Pummel(Card):
    """Deal damage multiple times"""
    
    # Card attributes
    card_type = "Attack"
    rarity = RarityType.RARE
    
    # Card values
    base_cost = 1
    base_damage = 2
    base_attack_times = 4
    
    # Upgrade values
    upgrade_attack_times = 5


@register("card")
class Uppercut(Card):
    """Deal damage and apply Vulnerable and Weak"""
    
    # Card attributes
    card_type = "Attack"
    rarity = RarityType.RARE
    
    # Card values
    base_cost = 2
    base_damage = 13
    base_magic = {"vulnerable": 2, "weak": 1}
    
    # Upgrade values
    upgrade_damage = 15
    upgrade_magic = {"vulnerable": 2, "weak": 2}
    
    def on_play(self, target: Creature | None = None) -> List[Action]:
        return super().on_play(target) + [
            ApplyPowerAction(target=target, power="vulnerable", amount=self.get_temp_value("magic_vulnerable")),
            ApplyPowerAction(target=target, power="weak", amount=self.get_temp_value("magic_weak"))
        ]


@register("card")
class Offering(Card):
    """Lose HP, gain Energy, Strength, and draw cards"""
    
    # Card attributes
    card_type = "Attack"
    rarity = RarityType.RARE
    
    # Card values
    base_cost = 0
    base_draw = 3
    base_energy_gain = 2
    
    # Upgrade values
    upgrade_draw = 5

    def on_play(self, target: Creature | None = None) -> List[Action]:
        return super().on_play(target) + [
            LoseHPAction(amount=6),
            GainEnergyAction(energy=self.get_temp_value("energy_gain")),
            AddCardAction(card=self, dest_pile="hand", amount=self.get_temp_value("draw"))
        ]
