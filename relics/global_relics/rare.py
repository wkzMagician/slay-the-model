"""
Rare Global Relics
Global relics available to all characters at rare rarity.
"""
from engine.runtime_api import add_action, add_actions
from typing import List
from actions.base import Action, LambdaAction
from actions.card import DrawCardsAction, AddCardAction, RemoveCardAction
from actions.combat import GainBlockAction, GainEnergyAction, HealAction, DealDamageAction, ApplyPowerAction, ModifyMaxHpAction
from relics.base import Relic
from utils.types import RarityType, CardType
from utils.registry import register
from utils.damage_phase import DamagePhase

# NOTE: AddGoldAction and other reward actions must be imported lazily inside methods
# to avoid circular import between actions.reward -> relics.base -> relics.global_relics.rare

@register("relic")
class BirdFacedUrn(Relic):
    """Whenever you play a Power card, heal 2 HP."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.RARE

    def on_card_play(self, card, player, targets):
        """When a Power is played, heal 2 HP"""
        if card.card_type == CardType.POWER:
            from engine.game_state import game_state
            add_actions([HealAction(target=player, amount=2)])
            return
        return
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
                from engine.game_state import game_state
                add_actions([GainBlockAction(block=18, target=player)])
                return
        return
@register("relic")
class DeadBranch(Relic):
    """Whenever you Exhaust a Card, add a random Card to your hand."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.RARE

    def on_card_exhausted(self, card, owner, source_pile=None):
        from actions.card import AddRandomCardAction

        if owner is None:
            return
        namespace = getattr(owner, "namespace", None)
        from engine.game_state import game_state
        add_actions([AddRandomCardAction(pile="hand", namespace=namespace)])
        return
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
            for card in game_state.player.card_manager.get_pile('draw_pile'):
                if card.card_type == CardType.CURSE:
                    curses += 1
        from engine.game_state import game_state
        add_actions([ApplyPowerAction(power="Strength", target=player, amount=curses)])
        return
@register("relic")
class FossilizedHelix(Relic):
    """Prevent first time you would lose HP in combat."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.RARE
    
    def on_combat_start(self, player, entities):
        """Apply Buffer power at combat start"""
        from engine.game_state import game_state
        add_actions([ApplyPowerAction(power="Buffer", target=player, amount=1, duration=-1)])
        return
@register("relic")
class Ginger(Relic):
    """You can no longer become Weakened."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.RARE

    def can_receive_power(self, power_name: str) -> bool:
        """Prevent Weak power from being applied"""
        if power_name.lower() in ("weak", "weakpower"):
            return False
        return True

@register("relic")
class Girya(Relic):
    """You can now gain Strength at Rest Sites. (3 times max)"""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.RARE
        self.uses_remaining = 3

    def on_trigger(self, **kwargs):
        """Triggered when player chooses Lift option at rest site"""
        if self.uses_remaining > 0:
            self.uses_remaining -= 1
            from engine.game_state import game_state
            from engine.game_state import game_state
            add_actions([ApplyPowerAction(power="Strength", target=game_state.player, amount=1)])
            return
        return
    def can_use_at_rest(self) -> bool:
        """Check if Girya can still be used"""
        return self.uses_remaining > 0

@register("relic")
class IceCream(Relic):
    """Energy is now conserved between turns."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.RARE
        self.conserved_energy = 0

    def on_player_turn_end(self, player, entities):
        """Store remaining energy at end of turn"""
        from engine.game_state import game_state
        if game_state.current_combat is not None:
            self.conserved_energy = game_state.player.energy
        return
    def on_player_turn_start(self, player, entities):
        """Add conserved energy at start of turn"""
        actions = []
        if self.conserved_energy > 0:
            actions.append(GainEnergyAction(energy=self.conserved_energy))
            self.conserved_energy = 0
        from engine.game_state import game_state
        add_actions(actions)
        return
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
            from engine.game_state import game_state
            add_actions([HealAction(target=player, amount=player.max_hp // 2)])
            return
        return
@register("relic")
class Mango(Relic):
    """Upon pickup, raise your Max HP by 14."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.RARE

    def on_obtain(self):
        from engine.game_state import game_state
        add_actions([ModifyMaxHpAction(amount=14)])
        return
@register("relic")
class OldCoin(Relic):
    """Gain 300 Gold."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.RARE

    def on_obtain(self):
        # Lazy import to avoid circular dependency
        from actions.reward import AddGoldAction
        from engine.game_state import game_state
        add_actions([AddGoldAction(amount=300)])
        return
@register("relic")
class PeacePipe(Relic):
    """You can now remove Cards from your deck at Rest Sites."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.RARE

    def can_use_at_rest(self) -> bool:
        """PeacePipe enables the remove card option at rest sites"""
        return True

@register("relic")
class Pocketwatch(Relic):
    """Whenever you play 3 or less Cards in a turn, draw 3 additional Cards at start of your next turn."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.RARE
        self.cards_played_this_turn = 0
        self.extra_draw_next_turn = False

    def on_card_play(self, card, player, targets):
        """Track cards played"""
        self.cards_played_this_turn += 1
        return
    def on_player_turn_end(self, player, entities):
        """Check cards played and set extra draw"""
        if self.cards_played_this_turn <= 3:
            self.extra_draw_next_turn = True
        return
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

    def modify_card_reward_count(self, base_count: int, combat_type: str) -> int:
        """Add an additional card reward for normal enemies"""
        if combat_type == "normal":
            return base_count + 1
        return base_count

@register("relic")
class Shovel(Relic):
    """You can now Dig for Relics at Rest Sites."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.RARE

    def can_use_at_rest(self) -> bool:
        """Shovel enables the dig option at rest sites"""
        return True

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
                from engine.game_state import game_state
                add_actions(actions)
                return
        return
@register("relic")
class ThreadAndNeedle(Relic):
    """At the start of each combat, gain 4 Plated Armor."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.RARE

    def on_combat_start(self, player, entities):
        """Gain 4 Plated Armor at start of combat"""
        from engine.game_state import game_state
        add_actions([ApplyPowerAction(power="PlatedArmor", target=player, amount=4)])
        return
@register("relic")
class Torii(Relic):
    """Whenever you receive 5 or less Attack damage, reduce it to 1."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.RARE
        self.damage_phase = DamagePhase.CAPPING  # Caps damage <=5 to 1
    
    def modify_damage_taken(self, base_damage: int, source=None) -> int:
        """Reduce attack damage <= 5 to 1."""
        # Note: This applies to all incoming damage <= 5
        # In the actual game, it only applies to Attack damage from enemies
        if base_damage <= 5 and base_damage > 0:
            return 1
        return base_damage

@register("relic")
class TungstenRod(Relic):
    """Whenever you lose HP, lose 1 less."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.RARE
        self.damage_phase = DamagePhase.ADDITIVE  # -1 to all damage
    
    def modify_damage_taken(self, base_damage: int, source=None) -> int:
        """Reduce all HP loss by 1."""
        if base_damage > 0:
            return max(0, base_damage - 1)
        return base_damage

@register("relic")
class Turnip(Relic):
    """Cannot be frail."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.RARE

    def can_receive_power(self, power_name: str) -> bool:
        """Prevent Frail power from being applied"""
        if power_name.lower() in ("frail", "frailpower"):
            return False
        return True

@register("relic")
class Calipers(Relic):
    """At the end of your turn, lose 15 Block rather than all of it."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.RARE
    
    # Block retention is handled in engine/combat.py
    # The combat system checks for Calipers and reduces block by 15 instead of resetting to 0


@register("relic")
class UnceasingTop(Relic):
    """Whenever you have no Cards in hand during your turn, draw a Card."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.RARE
        self.triggered_this_empty = False

    def on_card_play(self, card, player, targets):
        """Check if hand is empty after playing a card"""
        from engine.game_state import game_state
        if game_state.current_combat is not None:
            hand = game_state.player.card_manager.get_pile('hand')
            if len(hand) == 0 and not self.triggered_this_empty:
                self.triggered_this_empty = True
                from engine.game_state import game_state
                add_actions([DrawCardsAction(count=1)])
                return
        return
    def on_player_turn_start(self, player, entities):
        """Reset tracker at start of turn"""
        self.triggered_this_empty = False
        return