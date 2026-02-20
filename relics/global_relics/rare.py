"""
Rare Global Relics
Global relics available to all characters at rare rarity.
"""
from typing import List
from actions.base import Action, LambdaAction
from actions.card import DrawCardsAction, AddCardAction, RemoveCardAction
from actions.combat import GainBlockAction, GainEnergyAction, HealAction, DealDamageAction, ApplyPowerAction, ModifyMaxHpAction
from relics.base import Relic
from utils.types import RarityType, CardType
from utils.registry import register

# NOTE: AddGoldAction and other reward actions must be imported lazily inside methods
# to avoid circular import between actions.reward -> relics.base -> relics.global_relics.rare

@register("relic")
class BirdFacedUrn(Relic):
    """Whenever you play a Power card, heal 2 HP."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.RARE

    def on_card_play(self, card, player, entities):
        """When a Power is played, heal 2 HP"""
        if card.card_type == CardType.POWER:
            return [HealAction(target=player, amount=2)]
        return []

@register("relic")
class Calipers(Relic):
    """At the start of your turn, lose 15 Block rather than all of your Block."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.RARE

    # Implement in player's on_turn_end or combat flow

@register("relic")
class CaptainsWheel(Relic):
    """At the start of your 3rd turn, gain 18 Block."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.RARE

    def on_player_turn_start(self, player, entities):
        """At the start of your 3rd turn, gain 18 Block"""
        from engine.game_state import game_state
        if game_state.current_combat is not None:
            if game_state.current_combat.combat_state.combat_turn == 3:
                return [GainBlockAction(block=18, target=player)]
        return []

@register("relic")
class DeadBranch(Relic):
    """Whenever you Exhaust a Card, add a random Card to your hand."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.RARE

    def on_card_exhaust(self, card, player, entities):
        """When a card is exhausted, add random card to hand"""
        from actions.card import AddRandomCardAction
        from engine.game_state import game_state
        return [AddRandomCardAction(pile='hand', namespace=game_state.player.namespace)]

@register("relic")
class DuVuDoll(Relic):
    """For each Curse in your deck, start each combat with 1 additional Strength."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.RARE

    def on_combat_start(self, player, entities):
        """Gain additional Strength based on curses in deck"""
        from engine.game_state import game_state
        # Count curses in draw pile
        curses = 0
        if game_state.player:
            for card in game_state.player.card_manager.get_pile('draw'):
                if card.card_type == CardType.CURSE:
                    curses += 1
        return [ApplyPowerAction(power="Strength", target=player, amount=curses)]

@register("relic")
class FossilizedHelix(Relic):
    """Prevent first time you would lose HP in combat."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.RARE
    
    def on_combat_start(self, player, entities):
        """Apply Buffer power at combat start"""
        return [ApplyPowerAction(power="Buffer", target=player, amount=1, duration=-1)]

@register("relic")
class Ginger(Relic):
    """You can no longer become Weakened."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.RARE

    # This would need to hook into Weak application events
    # For now, implemented as a passive effect description
    # Implement in ApplyPowerAction (check if power is Weak)

@register("relic")
class Girya(Relic):
    """You can now gain Strength at Rest Sites. (3 times max)"""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.RARE
        self.uses_remaining = 3

    # This would need to hook into rest events
    # For now, implemented as a passive effect description

@register("relic")
class IceCream(Relic):
    """Energy is now conserved between turns."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.RARE

    # This would need to hook into turn end/start events
    # For now, implemented as a passive effect description
    # Implement in energy system (modify player?)

@register("relic")
class LizardTail(Relic):
    """When you would die, heal to 50% of your Max HP instead (works once)."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.RARE
        self.can_revive = True

    def on_death(self, damage, source, player, entities):
        """Revive when would die"""
        from engine.game_state import game_state
        if self.can_revive:
            self.can_revive = False
            return [HealAction(target=player, amount=player.max_hp // 2)]
        return []

@register("relic")
class MagicFlower(Relic):
    """Healing is 50% more effective during combat."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.RARE

    # This would need to hook into healing events
    # For now, implemented as a passive effect description

@register("relic")
class Mango(Relic):
    """Upon pickup, raise your Max HP by 14."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.RARE

    def on_obtain(self) -> List[Action]:
        return [ModifyMaxHpAction(amount=14)]

@register("relic")
class OldCoin(Relic):
    """Gain 300 Gold."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.RARE

    def on_obtain(self) -> List[Action]:
        # Lazy import to avoid circular dependency
        from actions.reward import AddGoldAction
        return [AddGoldAction(amount=300)]

@register("relic")
class PeacePipe(Relic):
    """You can now remove Cards from your deck at Rest Sites."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.RARE

    # This would need to hook into rest events
    # For now, implemented as a passive effect description

@register("relic")
class Pocketwatch(Relic):
    """Whenever you play 3 or less Cards in a turn, draw 3 additional Cards at start of your next turn."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.RARE
        self.cards_played_this_turn = 0
        self.extra_draw_next_turn = False

    def on_card_play(self, card, player, entities) -> List[Action]:
        """Track cards played"""
        self.cards_played_this_turn += 1
        return []

    def on_player_turn_end(self, player, entities):
        """Check cards played and set extra draw"""
        if self.cards_played_this_turn <= 3:
            self.extra_draw_next_turn = True
        return []

    def on_player_turn_start(self, player, entities):
        """Draw extra cards if condition met"""
        action = []
        if self.extra_draw_next_turn:
            action = [DrawCardsAction(count=3)]
        self._reset_trackers()
        return action

    def _reset_trackers(self):
        self.cards_played_this_turn = 0
        self.extra_draw_next_turn = False

@register("relic")
class PrayerWheel(Relic):
    """Normal enemies drop an additional Card reward."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.RARE

    # This would need to hook into enemy death/reward events
    # For now, implemented as a passive effect description

@register("relic")
class Shovel(Relic):
    """You can now Dig for Relics at Rest Sites."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.RARE

    # This would need to hook into rest events
    # For now, implemented as a passive effect description

@register("relic")
class StoneCalendar(Relic):
    """At the end of turn 7, deal 52 damage to ALL enemies."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.RARE

    def on_player_turn_end(self, player, entities):
        """Deal 52 damage at turn 7"""
        from engine.game_state import game_state
        if game_state.current_combat is not None:
            if game_state.current_combat.combat_state.combat_turn == 7:
                actions = []
                for enemy in entities:
                    actions.append(DealDamageAction(damage=52, target=enemy))
                return actions
        return []

@register("relic")
class TheSpecimen(Relic):
    """Whenever an enemy dies, transfer any Poison it has to a random enemy."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.RARE

    def on_damage_dealt(self, damage, target, player, entities):
        """Transfer Poison when enemy dies"""
        if target.is_dead():
            # Find Poison power on target
            poison_amount = 0
            for power in target.powers:
                if power.idstr == 'PoisonPower':
                    poison_amount = power.amount
                    break
            if poison_amount > 0:
                # Transfer to random alive enemy
                alive_enemies = [e for e in entities if not e.is_dead()]
                if alive_enemies:
                    import random
                    target_enemy = random.choice(alive_enemies)
                    return [ApplyPowerAction(power="Poison", target=target_enemy, amount=poison_amount)]
        return []

@register("relic")
class ThreadAndNeedle(Relic):
    """At the start of each combat, gain 4 Plated Armor."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.RARE

    def on_combat_start(self, player, entities):
        """Gain 4 Plated Armor at start of combat"""
        return [ApplyPowerAction(power="PlatedArmor", target=player, amount=4)]

@register("relic")
class Tingsha(Relic):
    """Whenever you discard a card during your turn, deal 3 damage to a random enemy for each card discarded."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.RARE

    def on_card_discard(self, card, player, entities):
        """Deal damage on discard"""
        from engine.game_state import game_state
        assert game_state.current_combat is not None
        alive_enemies = [e for e in game_state.current_combat.enemies if not e.is_dead()]
        if alive_enemies:
            import random
            target_enemy = random.choice(alive_enemies)
            return [DealDamageAction(damage=3, target=target_enemy)]
        return []

@register("relic")
class Torii(Relic):
    """Whenever you would receive 5 or less unblocked Attack damage, reduce it to 1."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.RARE

    # This would need to hook into damage calculation
    # For now, implemented as a passive effect description

@register("relic")
class ToughBandages(Relic):
    """Whenever you discard a Card during your turn, gain 3 Block."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.RARE

    def on_card_discard(self, card, player, entities):
        """Gain Block on card discard"""
        return [GainBlockAction(block=3, target=player)]

@register("relic")
class TungstenRod(Relic):
    """Whenever you would lose HP, lose 1 less."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.RARE

    # This would need to hook into damage calculation
    # For now, implemented as a passive effect description

@register("relic")
class Turnip(Relic):
    """Cannot be frail."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.RARE

    # This would need to hook into Weak application events
    # For now, implemented as a passive effect description
    # Implement in ApplyPowerAction (check if power is Frail)

@register("relic")
class UnceasingTop(Relic):
    """Whenever you have no Cards in hand during your turn, draw a Card."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.RARE

    # Implement in combat flow
