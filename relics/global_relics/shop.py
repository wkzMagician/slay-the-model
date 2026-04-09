"""
Shop Relics
Relics available only at shop.
"""
from engine.runtime_api import add_action, add_actions
from typing import List
from actions.base import Action, LambdaAction
from actions.card import ChooseCopyCardAction, ChooseObtainCardAction, DrawCardsAction
from actions.combat import GainBlockAction, GainEnergyAction, HealAction, DealDamageAction, ApplyPowerAction, ModifyMaxHpAction
from relics.base import Relic
from utils.types import RarityType, CardType
from utils.registry import register

# NOTE: AddRandomPotionAction must be imported lazily inside methods
# to avoid circular import between actions.reward -> relics.base -> relics.global_relics.shop

@register("relic")
class Cauldron(Relic):
    """Upon pickup, brews 5 random Potions."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.SHOP
    
    def on_obtain(self):
        # Lazy import to avoid circular dependency
        from actions.reward import AddRandomPotionAction
        from engine.game_state import game_state
        actions = []
        for _ in range(5):
            actions.append(AddRandomPotionAction(game_state.player.namespace))
        from engine.game_state import game_state
        add_actions(actions)
        return
@register("relic")
class ChemicalX(Relic):
    """Whenever you play a cost X Card, its effects are increased by 2."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.SHOP

    def modify_x_cost_card_effect(self, base_x: int) -> int:
        """Increase X value for card effects by 2."""
        return base_x + 2


@register("relic")
class ClockworkSouvenir(Relic):
    """At the start of each combat, gain 1 Artifact."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.SHOP

    def on_combat_start(self, floor: int):
        """Gain 1 Artifact at start of combat"""
        from engine.game_state import game_state
        player = game_state.player
        if player is None:
            return
        add_actions([ApplyPowerAction(power="Artifact", target=player, amount=1)])
        return
@register("relic")
class DollysMirror(Relic):
    """Upon pickup, obtain an additional copy of a Card in your deck."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.SHOP
        self.copied_card = None  # Would be set on pickup
        
    def on_obtain(self):
        from engine.game_state import game_state
        add_actions([ChooseCopyCardAction(pile='deck', copies=1)])
        return
@register("relic")
class FrozenEye(Relic):
    """When viewing your Drawpile, Cards are now shown in order."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.SHOP

    def can_view_draw_pile_order(self) -> bool:
        """Whether draw pile order should be visible."""
        return True


@register("relic")
class HandDrill(Relic):
    """Whenever you break an enemy's Block, apply 2 Vulnerable."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.SHOP

    def on_damage_dealt(self, damage, target, source=None, card=None, damage_type="direct"):
        from engine.game_state import game_state
        add_actions(
        [ApplyPowerAction(power="Vulnerable", target=target,
                                 amount=2, duration=2)]
        )
        return

@register("relic")
class LeesWaffle(Relic):
    """Raise your Max HP by 7 and heal all of your HP."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.SHOP

    def on_obtain(self):
        from engine.game_state import game_state
        from engine.game_state import game_state
        add_actions(
        [ModifyMaxHpAction(amount=7),
                HealAction(amount=game_state.player.max_hp)]
        )
        return

@register("relic")
class MedicalKit(Relic):
    """Status Cards can now be played. Playing a Status will Exhaust Card."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.SHOP

    def can_play_status_cards(self) -> bool:
        """Allow Status cards to be played."""
        return True

    def should_exhaust_status_on_play(self) -> bool:
        """Played Status cards should exhaust."""
        return True


@register("relic")
class MembershipCard(Relic):
    """50% discount on all products in Shop!"""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.SHOP

    # This hook into shop price calculations

@register("relic")
class PrismaticShard(Relic):
    """Combat reward screens now contain colorless cards and cards from other colors."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.SHOP

    def enables_all_color_card_pool(self) -> bool:
        """Allow card rewards to use all colors."""
        return True


@register("relic")
class Orrery(Relic):
    """Choose and add 5 Cards to your deck."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.SHOP

    def on_obtain(self):
        from engine.game_state import game_state

        has_prismatic_shard = any(
            getattr(relic, "idstr", None) == "PrismaticShard"
            for relic in game_state.player.relics
        )
        reward_namespace = None if has_prismatic_shard else game_state.player.namespace

        actions = []
        for _ in range(5):
            actions.append(ChooseObtainCardAction(
                total=3,
                namespace=reward_namespace,
                encounter_type="shop",
                use_rolling_offset=False,
            ))
        from engine.game_state import game_state
        add_actions(actions)
        return
@register("relic")
class SlingOfCourage(Relic):
    """Start each Elite combat with 2 Strength. (Does not work against Bosses)"""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.SHOP

    def on_combat_start(self, floor: int):
        """Start Elite combats with 2 Strength"""
        from engine.game_state import game_state
        from utils.types import CombatType
        
        combat = game_state.current_combat
        if combat is not None and combat.combat_type == CombatType.ELITE:
            player = game_state.player
            if player is None:
                return
            add_actions([ApplyPowerAction(power="Strength", target=player, amount=2)])
            return
        return
@register("relic")
class StrangeSpoonShop(Relic):
    """Cards which Exhaust when played will instead discard 50% of time."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.SHOP

    def should_prevent_exhaust(self, card=None) -> bool:
        """50% chance to discard a card instead of exhausting it."""
        import random

        return random.random() < 0.5


@register("relic")
class TheAbacus(Relic):
    """Gain 6 Block whenever you shuffle your Drawpile."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.SHOP

    def on_shuffle(self):
        """Gain 6 Block when shuffling draw pile."""
        from engine.game_state import game_state
        from engine.game_state import game_state
        add_actions([GainBlockAction(block=6, target=game_state.player)])
        return
@register("relic")
class Toolbox(Relic):
    """At the start of each combat, choose 1 of 3 random Colorless Cards and add the chosen Card into your hand."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.SHOP
    
    def on_combat_start(self, floor: int):
        """Add 1 random Colorless card to hand at start of combat"""
        from actions.card import AddRandomCardAction
        from engine.game_state import game_state
        # Add a random colorless card to hand with 0 cost for the turn
        from engine.game_state import game_state
        add_actions(
        [AddRandomCardAction(
            pile='hand', 
            namespace='colorless',
            cost_until_end_of_turn=0
        )]
        )
        return


@register("relic")
class StrikeDummy(Relic):
    """Strike cards deal 3 additional damage."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.SHOP
    
    def modify_damage_dealt(self, base_damage: int, card=None, target=None) -> int:
        """Add 3 damage to Strike cards."""
        if card and hasattr(card, 'card_type') and card.card_type == CardType.ATTACK:
            # Check if it's a Strike card by name pattern or card_id
            if hasattr(card, 'card_id') and 'strike' in card.card_id.lower():
                return base_damage + 3
        return base_damage


@register("relic")
class PotionBeltShop(Relic):
    """Gain 2 additional potion slots."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.SHOP
    
    def on_obtain(self):
        """Increase potion slots by 2."""
        from engine.game_state import game_state
        game_state.player.potion_slots += 2
        return
