from actions.base import Action
from typing import Optional, Callable, Any, List
from utils.result_types import BaseResult, BaseResult, NoneResult, SingleActionResult, MultipleActionsResult
from localization import t
from utils.registry import register
from entities.creature import Creature

@register("action")
class ModifyMaxHpAction(Action):
    """Modify player's max HP

    Required:
        amount (int): HP change amount

    Optional:
        None
    """
    def __init__(self, amount: int):
        self.amount = amount

    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state
        if game_state.player:
            game_state.player.max_hp += self.amount
            print(t("ui.max_hp_changed", default=f"Max HP changed by {self.amount}!", amount=self.amount))
        return NoneResult()

@register("action")
class LoseHpAction(Action):
    """Modify player's HP

    Required:
        amount (int): HP change amount

    Optional:
        None
    """
    def __init__(self, amount: int):
        self.amount = amount

    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state
        if game_state.player:
            game_state.player.hp -= self.amount
        return NoneResult()

@register("action")
class DealDamageAction(Action):
    """Deal damage to a target

    Required:
        damage (int or callable): Damage amount to deal
        target (Creature): Target creature

    Optional:
        damage_type (str): Type of damage ("direct", "attack", etc.)
        card (Card): Card that caused the damage (for power triggers)
        source (Creature): Source of the damage
    """
    def __init__(self, name: str, damage, target: Creature,
                 damage_type: str = "direct", card=None, source=None):
        self.name = name
        self._damage = damage
        self.target = target
        self.damage_type = damage_type
        self.card = card
        self.source = source

    @property
    def damage(self) -> int:
        """Get damage amount (handles callable)"""
        if callable(self._damage):
            return self._damage()
        return int(self._damage)

    def execute(self):
        from engine.game_state import game_state

        # Get source status (for strength)
        source_strength = 0
        if self.source:
            source_status = game_state.combat_state.get_entity_status(self.source)
            source_strength = source_status.get("strength", 0)

        # Apply strength to damage
        base_damage = self.damage
        if source_strength != 0:
            base_damage = max(0, base_damage + source_strength)

        # Apply weak modifier to damage
        final_damage = base_damage
        if self.target and not self.target.is_dead():
            target_status = game_state.combat_state.get_entity_status(self.target)

            # Check for artifact (prevents status effects)
            artifact_count = target_status.get("artifact", 0)

            if target_status.get("weak", 0) > 0 and self.damage_type == "direct":
                # Weak: 25% damage reduction
                # If artifact > 0, block the debuff
                if artifact_count > 0:
                    # Prevent weak from being applied
                    final_damage = base_damage
                else:
                    final_damage = int(base_damage * 0.75)
                    if final_damage < 1 and base_damage > 0:
                        final_damage = 1

        # Deal damage
        if self.target:
            damage_dealt = self.target.take_damage(
                final_damage,
                source=self.source,
                card=self.card,
                damage_type=self.damage_type
            )

            # Apply vulnerable (makes next attack deal more damage)
            if damage_dealt > 0:
                status = game_state.combat_state.get_entity_status(self.target)
                if status.get("vulnerable", 0) > 0:
                    # Vulnerable: next attack deals 50% more damage
                    # This is handled in the attacker's next damage calculation
                    pass

        return NoneResult()

@register("action")
class GainBlockAction(Action):
    """Gain block for a creature

    Required:
        block (int or callable): Block amount to gain

    Optional:
        target (Creature): Target to gain block (defaults to player)
        card (Card): Card that caused the block gain
        source (Creature): Source of the block
    """
    def __init__(self, block, target: Optional[Creature] = None, card=None, source=None):
        self._block = block
        self.target = target
        self.card = card
        self.source = source

    @property
    def block(self) -> int:
        """Get block amount (handles callable)"""
        if callable(self._block):
            return self._block()
        return int(self._block)

    def execute(self):
        from engine.game_state import game_state

        # Determine target
        target = self.target or game_state.player
        if not target or target.is_dead():
            return NoneResult()

        # Apply frail modifier to block
        final_block = self.block
        if target is game_state.player:
            status = game_state.combat_state.get_entity_status(target)

            # Check for artifact (prevents status effects)
            artifact_count = status.get("artifact", 0)

            if status.get("frail", 0) > 0:
                # Frail: 25% block reduction
                # If artifact > 0, block the debuff
                if artifact_count > 0:
                    # Prevent frail from being applied
                    final_block = self.block
                else:
                    final_block = int(self.block * 0.75)
                    if final_block < 1 and self.block > 0:
                        final_block = 1

        # Gain block
        target.gain_block(final_block, source=self.source, card=self.card)

        # Trigger on_block powers
        if hasattr(target, 'powers'):
            for power in list(target.powers):
                if hasattr(power, "on_gain_block"):
                    power.on_gain_block(final_block, player=target, source=self.source, card=self.card)

        return NoneResult()

@register("action")
class DrawCardsAction(Action):
    """Draw cards from draw pile

    Required:
        count (int or callable): Number of cards to draw

    Optional:
        None
    """
    def __init__(self, count):
        self._count = count

    @property
    def count(self) -> int:
        """Get count (handles callable)"""
        if callable(self._count):
            return self._count()
        return int(self._count)

    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state

        if game_state.player and hasattr(game_state.player, "card_manager"):
            cards = game_state.player.card_manager.draw(self.count)
            return MultipleActionsResult(cards)

        return MultipleActionsResult([])

@register("action")
class GainEnergyAction(Action):
    """Gain energy for player

    Required:
        energy (int or callable): Energy amount to gain

    Optional:
        None
    """
    def __init__(self, energy):
        self._energy = energy

    @property
    def energy(self) -> int:
        """Get energy (handles callable)"""
        if callable(self._energy):
            return self._energy()
        return int(self._energy)

    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state

        if game_state.player:
            game_state.player.gain_energy(self.energy)
            return SingleActionResult(game_state.player.energy)

        return NoneResult()

@register("action")
class PlayCardAction(Action):
    """Play a card from hand

    Required:
        card (Card): Card to play
        target (Creature): Target creature (optional for self-targeting cards)

    Optional:
        None
    """
    def __init__(self, card, target: Optional[Creature] = None):
        self.card = card
        self.target = target

    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state

        if not self.card:
            return NoneResult()

        # Check if card can be played
        can_play, reason = self.card.can_play()
        if not can_play:
            print(f"Cannot play card: {reason}")
            return NoneResult()

        # Spend energy
        cost = self.card.get_temp_value('cost')
        from actions.combat import GainEnergyAction
        if cost > 0:
            game_state.player.gain_energy(-cost)
            game_state.combat_state.player_energy_spent_this_turn += cost

        # Update turn tracking
        game_state.combat_state.turn_cards_played += 1
        game_state.combat_state.player_actions_this_turn += 1

        # Trigger on_play_card powers
        if hasattr(game_state.player, 'powers'):
            for power in list(game_state.player.powers):
                if hasattr(power, "on_play_card"):
                    result = power.on_play_card(self.card)
                    if result and isinstance(result, list):
                        return MultipleActionsResult(result)

        # Get card actions
        actions = self.card.on_play(self.target)

        # Remove card from hand
        from actions.card import ExhaustCardAction
        if self.card.get_temp_value('exhaust'):
            actions.insert(0, ExhaustCardAction(card=self.card, source_pile="hand"))
        else:
            # Move to discard pile
            from actions.card import RemoveCardAction, AddCardAction
            actions.insert(0, RemoveCardAction(card=self.card, src_pile="hand"))
            actions.append(AddCardAction(card=self.card, dest_pile="discard"))

        return MultipleActionsResult(actions)

@register("action")
class EndTurnAction(Action):
    """End player turn

    Required:
        None

    Optional:
        None
    """
    def __init__(self):
        pass

    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state

        # Transition to enemy action phase
        game_state.combat_state.current_phase = "enemy_action"

        # This will be handled by Combat._build_turn_actions()
        return NoneResult()

@register("action")
class HealAction(Action):
    """Heal a creature

    Required:
        heal (int or callable): Heal amount

    Optional:
        target (Creature): Target to heal (defaults to player)
    """
    def __init__(self, heal, target: Optional[Creature] = None):
        self._heal = heal
        self.target = target

    @property
    def heal(self) -> int:
        """Get heal amount (handles callable)"""
        if callable(self._heal):
            return self._heal()
        return int(self._heal)

    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state

        target = self.target or game_state.player
        if target:
            target.heal(self.heal)
            return SingleActionResult(target.hp)

        return NoneResult()

@register("action")
class ApplyStatusAction(Action):
    """Apply status effect to a creature

    Required:
        status_type (str): Type of status ("weak", "vulnerable", "frail", "strength")
        amount (int): Amount to apply

    Optional:
        target (Creature): Target creature (defaults to player)
    """
    def __init__(self, status_type: str, amount: int, target: Optional[Creature] = None):
        self.status_type = status_type
        self.amount = amount
        self.target = target

    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state

        target = self.target or game_state.player
        if target:
            game_state.combat_state.apply_status(target, self.status_type, self.amount)
            return NoneResult()

        return NoneResult()