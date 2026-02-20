"""
Event Relics
Relics obtained through events.
"""
from typing import List
from actions.base import Action, LambdaAction
from actions.card import ChooseAddRandomCardAction
from actions.combat import GainBlockAction, GainEnergyAction, HealAction, DealDamageAction, ApplyPowerAction, ModifyMaxHpAction
# GainGoldAction imported lazily when needed to avoid circular import
from relics.base import Relic
from utils.types import CardType, RarityType
from utils.registry import register

@register("relic")
class CultistHeadpiece(Relic):
    """CAW CAW CAWWWW!"""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.EVENT

    # This is a cosmetic relic with no effect
    # Implemented as a passive effect description

@register("relic")
class FaceOfCleric(Relic):
    """Raise your Max HP by 1 after each combat."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.EVENT

    def on_combat_end(self, player, entities):
        """Raise Max HP by 1 after combat"""
        from actions.combat import ModifyMaxHpAction
        return [ModifyMaxHpAction(amount=1)]

@register("relic")
class GoldenIdol(Relic):
    """Enemies drop 25% more Gold."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.EVENT

    # This would need to hook into enemy death/reward events
    # For now, implemented as a passive effect description

@register("relic")
class BloodyIdol(Relic):
    """Whenever you gain Gold, heal 5 HP."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.EVENT

    # This would need to hook into gold gain events
    # For now, implemented as a passive effect description
    # Implement in AddGoldAction

@register("relic")
class GremlinVisage(Relic):
    """Start each combat with 1 Weak."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.EVENT

    def on_combat_start(self, player, entities):
        """Apply 1 Weak at start of combat"""
        actions = []
        for enemy in entities:
            actions.append(ApplyPowerAction(power="Weak", target=enemy, amount=1, duration=2))
        return actions

@register("relic")
class MarkOfBloom(Relic):
    """You can no longer heal."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.EVENT

    # This would need to hook into healing events
    # For now, implemented as a passive effect description
    # Implement in HealAction

@register("relic")
class MutagenicStrength(Relic):
    """Start each combat with 3 Strength that is lost at end of your turn."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.EVENT

    def on_player_turn_start(self, player, entities) -> List[Action]:
        # todo: ApplyPowerAction, Strength and StrengthDown
        return []

@register("relic")
class Necronomicon(Relic):
    """The first Attack played each turn that costs 2 or more is played twice. When you take this Relic, become Cursed."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.EVENT
        self.double_attack_played = False

    def on_turn_start(self, player, entities) -> List[Action]:
        """Reset tracker at start of combat"""
        return [LambdaAction(func=lambda: setattr(self, 'double_attack_played', False))]

    def on_card_play(self, card, player, entities):
        """Track high-cost attacks and play twice"""
        if card.cost >= 2 and card.card_type == CardType.ATTACK and not self.double_attack_played:
            self.double_attack_played = True
            return card.on_play() * 1
        return []

@register("relic")
class NilrysCodex(Relic):
    """At end of each turn, you can choose 1 of 3 random Cards to shuffle into your Drawpile."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.EVENT

    def on_player_turn_end(self, player, entities) -> List[Action]:
        from engine.game_state import game_state
        return [ChooseAddRandomCardAction(pile='draw_pile', namespace=game_state.player.namespace)]

@register("relic")
class Enchiridion(Relic):
    """At the start of each combat, add a random Power to your hand. It costs 0 Energy until end of turn."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.EVENT

    # todo: on_combat_start, AddRandomCardAction

@register("relic")
class NeowsLament(Relic):
    """Enemies in your first 3 combats will have 1 HP."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.EVENT
        self.combat_count = 0

    def on_combat_start(self, player, entities):
        """Set enemy HP to 1 for first 3 combats"""
        if self.combat_count < 3:
            self.combat_count += 1
            actions = []
            for enemy in entities:
                actions.append(ModifyMaxHpAction(amount=-enemy.max_hp + 1))
            return actions
        return []

@register("relic")
class NlothHungryFace(Relic):
    """The next non-boss chest you open is empty."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.EVENT
        self.chest_spawned = False

    # This would need to hook into chest opening events
    # For now, implemented as a passive effect description

@register("relic")
class OddMushroom(Relic):
    """When Vulnerable, take 25% more damage rather than 50%."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.EVENT

    # This would need to hook into damage calculation
    # For now, implemented as a passive effect description

@register("relic")
class SsserpentHead(Relic):
    """Whenever you enter an Event room, gain 50 Gold."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.EVENT

    # This would need to hook into room entry events
    # For now, implemented as a passive effect description

@register("relic")
class WarpedTongs(Relic):
    """At the start of your turn, Upgrade a random Card in your hand for rest of combat."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.EVENT
        
    # ! distinguish on_player_turn_start (pre-draw or post-draw)

    # todo: UpgradeRandomCardAction
    # Hint: exclude ungradable cards

@register("relic")
class RedMask(Relic):
    """At the start of each combat, apply 1 Weakness to ALL enemies."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.EVENT

    def on_combat_start(self, player, entities):
        """Apply 1 Weak to all enemies at start of combat"""
        actions = []
        for enemy in entities:
            actions.append(ApplyPowerAction(power="Weak", target=enemy, amount=1, duration=2))
        return actions

@register("relic")
class NlothGift(Relic):
    """Triples chance of receiving rare Cards as monster rewards."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.EVENT

    # This would need to hook into card reward generation
    # For now, implemented as a passive effect description
    
    # Influence get_random_card_reward
