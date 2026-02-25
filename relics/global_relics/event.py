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

    def modify_gold_gained(self, base_gold: int) -> int:
        """Increase gold gained by 25%."""
        return int(base_gold * 1.25)

@register("relic")
class BloodyIdol(Relic):
    """Whenever you gain Gold, heal 5 HP."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.EVENT

    def on_gold_gained(self, gold_amount: int, player) -> List[Action]:
        """Heal 5 HP when gold is gained."""
        return [HealAction(target=player, amount=5)]

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

    def modify_heal(self, base_heal: int) -> int:
        """Completely prevent healing."""
        return 0

@register("relic")
class MutagenicStrength(Relic):
    """Start each combat with 3 Strength that is lost at end of your turn."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.EVENT

    def on_combat_start(self, player, entities) -> List[Action]:
        """Gain 3 Strength at combat start (will be removed at turn end)"""
        return [ApplyPowerAction(power="Strength", target=player, amount=3)]
    
    def on_player_turn_end(self, player, entities) -> List[Action]:
        """Remove all Strength at turn end"""
        from actions.combat import RemovePowerAction
        # Remove all gained Strength (would need to track amount gained)
        # Simplified: remove 3 Strength
        return [ApplyPowerAction(power="Strength", target=player, amount=-3)]

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
    """At start of each combat, add a random Power to your hand. It costs 0 Energy until end of turn."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.EVENT

    def on_combat_start(self, player, entities):
        """Add a random Power to hand with 0 cost"""
        from actions.card import AddRandomCardAction
        from engine.game_state import game_state
        from utils.types import CardType
        
        return [AddRandomCardAction(
            pile='hand',
            card_type=CardType.POWER,
            namespace=game_state.player.namespace,
            temp_cost=0
        )]

@register("relic")
class NeowsLament(Relic):
    """Enemies in your first 3 combats will have 1 HP."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.EVENT
        self.combat_count = 0
        self.uses_remaining = 3

    def on_combat_start(self, player, entities):
        """Set enemy HP to 1 for first 3 combats"""
        if self.uses_remaining > 0:
            self.uses_remaining -= 1
            actions = []
            for enemy in entities:
                # Set current HP to 1, not max HP
                enemy.hp = 1
            return actions
        return []

@register("relic")
class NlothHungryFace(Relic):
    """The next non-boss chest you open is empty."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.EVENT
        self.chest_consumed = False

    def should_empty_chest(self, chest_type: str = None) -> bool:
        """The next non-boss chest opened by player is empty."""
        if self.chest_consumed:
            return False
        if chest_type == "boss":
            return False
        self.chest_consumed = True
        return True

@register("relic")
class OddMushroom(Relic):
    """When Vulnerable, take 25% more damage rather than 50%."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.EVENT
    
    def modify_damage_taken(self, base_damage: int, source=None) -> int:
        """Reduce Vulnerable damage from 50% to 25%."""
        from engine.game_state import game_state

        player = getattr(game_state, "player", None)
        if not player:
            return base_damage

        for power in getattr(player, "powers", []):
            if getattr(power, "name", "") == "Vulnerable":
                # Vulnerable multiplier has already been applied (x1.5).
                # Convert to x1.25 by multiplying by 5/6.
                return int(base_damage * 5 / 6)
        return base_damage

@register("relic")
class SsserpentHead(Relic):
    """Whenever you enter an Event room, gain 50 Gold."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.EVENT

    # This hook into room entry events

@register("relic")
class WarpedTongs(Relic):
    """At start of your turn, Upgrade a random Card in your hand for rest of combat."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.EVENT
        
    def on_player_turn_start(self, player, entities):
        """Upgrade a random card in hand for rest of combat"""
        from actions.card import UpgradeRandomCardAction
        from engine.game_state import game_state
        
        hand = game_state.player.card_manager.get_pile('hand')
        if hand:
            # Upgrade a random upgradable card in hand
            return [UpgradeRandomCardAction(count=1, namespace=game_state.player.namespace)]
        return []

@register("relic")
class RedMask(Relic):
    """At start of each combat, apply 1 Weakness to ALL enemies."""
    
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

    def modifies_card_reward_rare_chance(self) -> bool:
        """Marker hook for get_random_card_reward."""
        return True


@register("relic")
class SpiritPoop(Relic):
    """Obtained from Bonfire Spirits when sacrificing a Curse."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.EVENT
    
    # This is a cosmetic relic with no gameplay effect
    # It represents a curse "reward" from spirits