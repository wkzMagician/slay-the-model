"""
Shop Relics
Relics available only at shop.
"""
from typing import List
from actions.base import Action, LambdaAction
from actions.card import ChooseAddRandomCardAction, ChooseCopyCardAction, DrawCardsAction
from actions.combat import GainBlockAction, GainEnergyAction, HealAction, DealDamageAction, ApplyPowerAction, ModifyMaxHpAction
# GainGoldAction imported lazily when needed to avoid circular import
from actions.reward import AddRandomPotionAction
from relics.base import Relic
from utils.types import RarityType, CardType
from utils.registry import register

@register("relic")
class Cauldron(Relic):
    """Upon pickup, brews 5 random Potions."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.SHOP
    
    def on_obtain(self) -> List[Action]:
        from engine.game_state import game_state
        actions = []
        for _ in range(5):
            actions.append(AddRandomPotionAction(game_state.player.namespace))
        return actions

@register("relic")
class ChemicalX(Relic):
    """Whenever you play a cost X Card, its effects are increased by 2."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.SHOP
    
    # This would need to hook into card cost calculations
    # For now, implemented as a passive effect description

@register("relic")
class ClockworkSouvenir(Relic):
    """At the start of each combat, gain 1 Artifact."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.SHOP

    def on_combat_start(self, player, entities):
        """Gain 1 Artifact at start of combat"""
        return [ApplyPowerAction(power="Artifact", target=player, amount=1)]

@register("relic")
class DollysMirror(Relic):
    """Upon pickup, obtain an additional copy of a Card in your deck."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.SHOP
        self.copied_card = None  # Would be set on pickup
        
    def on_obtain(self) -> List[Action]:
        return [ChooseCopyCardAction(pile='deck', copies=1)]

@register("relic")
class FrozenEye(Relic):
    """When viewing your Drawpile, Cards are now shown in order."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.SHOP

    # This would need to hook into draw pile viewing
    # For now, implemented as a passive effect description

@register("relic")
class HandDrill(Relic):
    """Whenever you break an enemy's Block, apply 2 Vulnerable."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.SHOP

    def on_damage_dealt(self, damage, target, player, entities):
        return [ApplyPowerAction(power="Vulunerable", target=target, amount=2)]

@register("relic")
class LeesWaffle(Relic):
    """Raise your Max HP by 7 and heal all of your HP."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.SHOP

    def on_obtain(self) -> List[Action]:
        from engine.game_state import game_state
        return [ModifyMaxHpAction(amount=7),
                HealAction(amount=game_state.player.max_hp)]

@register("relic")
class MedicalKit(Relic):
    """Status Cards can now be played. Playing a Status will Exhaust Card."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.SHOP

    # This would need to hook into card play for status cards
    # For now, implemented as a passive effect description

@register("relic")
class MembershipCard(Relic):
    """50% discount on all products in Shop!"""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.SHOP

    # This would need to hook into shop price calculations
    # For now, implemented as a passive effect description

@register("relic")
class PrismaticShard(Relic):
    """Combat reward screens now contain colorless cards and cards from other colors."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.SHOP

    # This would need to hook into card reward generation
    # For now, implemented as a passive effect description

@register("relic")
class Orrery(Relic):
    """Choose and add 5 Cards to your deck."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.SHOP

    def on_obtain(self) -> List[Action]:
        from engine.game_state import game_state
        actions = []
        for _ in range(5):
            actions.append(ChooseAddRandomCardAction(pile='deck', namespace=game_state.player.namespace))
        return actions

# !!! massive refactor
# todo: 每一种遗物只存在一个类，不区分是否是Shop。
# e.g. 如果一个遗物同时是UNCOMMON和SHOP，那么只需要保留UNCOMMON的一份
# 特别建厂所有Shop结尾的遗物。如果有和其他遗物功能重复，则删除
@register("relic")
class PotionBeltShop(Relic):
    """Upon pick up, gain 2 Potion slots."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.SHOP

    # This would need to hook into relic pickup events
    # For now, implemented as a passive effect description

@register("relic")
class SlingOfCourage(Relic):
    """Start each Elite combat with 2 Strength. (Does not work against Bosses)"""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.SHOP

    # todo: on_combat_start

@register("relic")
class StrangeSpoonShop(Relic):
    """Cards which Exhaust when played will instead discard 50% of time."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.SHOP

    # This would need to hook into card exhaust events
    # For now, implemented as a passive effect description

@register("relic")
class TheAbacus(Relic):
    """Gain 6 Block whenever you shuffle your Drawpile."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.SHOP

    def on_shuffle(self) -> List[Action]:
        """Gain 6 Block when shuffling draw pile."""
        return [GainBlockAction(amount=6)]

@register("relic")
class TwistedFunnel(Relic):
    """At the start of each combat, apply 4 Poison to ALL enemies."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.SHOP
    
    def on_combat_start(self, player, entities):
        """Apply 4 Poison to all enemies at start of combat"""
        actions = []
        for enemy in entities:
            actions.append(ApplyPowerAction(power="Poison", target=enemy, amount=4, duration=3))
        return actions

@register("relic")
class Toolbox(Relic):
    """At the start of each combat, choose 1 of 3 random Colorless Cards and add the chosen Card into your hand."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.SHOP
    
    def on_combat_start(self, player, entities):
        """Add 1 random Colorless card to hand at start of combat"""
        # todo: ChooseAddRandomCardAction
        return []
