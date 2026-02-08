from actions.base import Action
from typing import Optional, Callable, Any, List, TYPE_CHECKING
from utils.result_types import BaseResult, BaseResult, NoneResult, SingleActionResult, MultipleActionsResult
from localization import t
from utils.registry import register
from entities.creature import Creature

if TYPE_CHECKING:
    from enemies.base import Enemy

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
class RemoveEnemyAction(Action):
    """Remove an enemy from combat

    Required:
        enemy (Enemy): Enemy to remove

    Optional:
        None
    """
    def __init__(self, enemy: 'Enemy'):
        self.enemy = enemy

    def execute(self) -> 'BaseResult':
        """Remove enemy from combat state"""
        from engine.game_state import game_state
        
        if game_state.combat_state:
            game_state.combat_state.remove_enemy(self.enemy)
        
        return NoneResult()


@register("action")
class AddEnemyAction(Action):
    """Add an enemy to combat

    Required:
        enemy (Enemy): Enemy to add

    Optional:
        None
    """
    def __init__(self, enemy: 'Enemy'):
        self.enemy = enemy

    def execute(self) -> 'BaseResult':
        """Add enemy to combat state"""
        from engine.game_state import game_state
        
        if game_state.combat_state:
            game_state.combat_state.add_enemy(self.enemy)
        
        return NoneResult()

@register("action")
class HealAction(Action):
    """Heal the player for a specified amount

    Required:
        amount (int): Amount to heal

    Optional:
        None
    """
    def __init__(self, amount: int):
        self.amount = amount

    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state
        if game_state.player:
            old_hp = game_state.player.hp
            game_state.player.hp = min(game_state.player.hp + self.amount, game_state.player.max_hp)
            healed = game_state.player.hp - old_hp
            print(t("ui.healed", default=f"Healed for {healed} HP.", amount=healed))
        return NoneResult()

@register("action")
class LoseHPAction(Action):
    """Deal damage to player

    Required:
        amount (int): Amount to lose

    Optional:
        None
    """
    def __init__(self, amount: int):
        self.amount = amount

    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state
        if game_state.player:
            old_hp = game_state.player.hp
            game_state.player.hp -= self.amount
            lost = old_hp - game_state.player.hp
            print(t("ui.lost_hp", default=f"Lost {lost} HP.", amount=lost))
        return NoneResult()

@register("action")
class DealDamageAction(Action):
    """Deal damage to a target (basic damage action)

    This action performs the core damage operation:
    - Calculate damage value (handles callable)
    - Reduce target HP (via Creature.take_damage which triggers power hooks)
    - Trigger relic damage hooks

    Complex damage modifiers (strength, weak, vulnerable, artifact, etc.)
    should be handled by AttackAction or similar higher-level actions.

    Required:
        damage (int or callable): Damage amount to deal
        target (Creature): Target creature

    Optional:
        damage_type (str): Type of damage ("direct", "attack", etc.)
        card (Card): Card that caused the damage (for power triggers)
        source (Creature): Source of the damage
    """
    def __init__(self, name: str, damage: int, target: Creature,
                 damage_type: str = "direct", card=None, source=None):
        self.name = name
        self.damage = damage
        self.target = target
        self.damage_type = damage_type
        self.card = card
        self.source = source

    def execute(self):
        from engine.game_state import game_state

        if not self.target or self.target.is_dead():
            return NoneResult()

        # Calculate damage value
        damage_amount = self.damage

        # Deal damage (this triggers power hooks via Creature.take_damage)
        damage_dealt = self.target.take_damage(
            damage_amount,
            source=self.source,
            card=self.card,
            damage_type=self.damage_type
        )
        
        # Trigger relic hooks before damage (on_damage_dealt)
        for relic in game_state.player.relics:
            if hasattr(relic, "on_damage_dealt"):
                actions = relic.on_damage_dealt(
                    damage=damage_amount,
                    target=self.target,
                    player=game_state.player,
                )
                if actions:
                    game_state.action_queue.add_actions(actions)

        return NoneResult()

@register("action")
class GainBlockAction(Action):
    """Gain block for a creature

    Required:
        block (int or callable): Block amount to gain
        target (Creature): Target to gain block (defaults to player)
    """
    def __init__(self, block, target: Creature):
        self.block = block
        self.target = target

    def execute(self):
        from engine.game_state import game_state

        self.target.gain_block(self.block, source=None, card=None)

        return NoneResult()

@register("action")
class GainEnergyAction(Action):
    """Gain energy for player

    Required:
        energy (int): Energy amount to gain

    Optional:
        None
    """
    def __init__(self, energy):
        self.energy = energy

    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state

        if game_state.player:
            game_state.player.gain_energy(self.energy)
            
        return NoneResult()

# todo: 支持从抽牌堆打出牌
# todo: 支持打出时无视费用
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
class ApplyPowerAction(Action):
    """Apply a power to a target creature

    Required:
        power (str or Power): Power name string or Power instance
        target (Creature): Target creature to apply power to
        amount (int): Power amount

    Optional:
        duration (int): Power duration (0 for permanent)
    """
    def __init__(self, power, target: Creature, amount: int, duration: int = 0):
        self.power = power
        self.target = target
        self.amount = amount
        self.duration = duration

    def execute(self) -> 'BaseResult':
        """Apply the power to the target creature"""
        from utils.registry import get_registered
        
        if not self.target:
            return NoneResult()

        # If power is a string, get the registered power class
        if isinstance(self.power, str):
            power_class = get_registered("power", self.power)
            if not power_class:
                print(f"Power {self.power} not found")
                return NoneResult()
            power_instance = power_class(amount=self.amount, duration=self.duration)
        else:
            # Already a Power instance
            power_instance = self.power

        # Apply the power to the target
        self.target.add_power(power_instance)
        
        return NoneResult()

@register("action")
class TriggerRelicAction(Action):
    """Trigger a relic's passive or active effect
    
    Required:
        relic_name (str): Name of relic to trigger
    
    Optional:
        None
    """
    def __init__(self, relic_name: str):
        self.relic_name = relic_name
    
    def execute(self) -> 'BaseResult':
        """Trigger a relic's effect"""
        from engine.game_state import game_state
        
        if not game_state.player:
            return NoneResult()
        
        # Find relic
        from utils.registry import get_registered
        relic = get_registered("relic", self.relic_name)
        if not relic:
            return NoneResult()
        
        # Trigger relic's effect
        # Relics implement their own trigger logic
        if hasattr(relic, "on_trigger"):
            relic.on_trigger()
        elif hasattr(relic, "passive"):
            relic.passive()
        
        return NoneResult()

