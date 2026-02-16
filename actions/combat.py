from actions.base import Action
from typing import Optional, Callable, Any, List, TYPE_CHECKING
from actions.card import DiscardCardAction
from utils.result_types import BaseResult, BaseResult, NoneResult, SingleActionResult, MultipleActionsResult
from localization import t
from utils.registry import register
from entities.creature import Creature

# Lazy import COST_X to avoid circular import
COST_X = -1  # Default value, will be overwritten when cards.base is loaded

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
        actions_to_return = []
        
        if game_state.player:
            old_max = game_state.player.max_hp
            game_state.player.max_hp += self.amount
            new_max = game_state.player.max_hp
            
            # Trigger on_max_hp_changed hook
            actions = game_state.player.on_max_hp_changed(old_max, new_max)
            if actions:
                actions_to_return.extend(actions)
            
            print(t("ui.max_hp_changed", default=f"Max HP changed by {self.amount}!", amount=self.amount))
        
        if actions_to_return:
            return MultipleActionsResult(actions_to_return)
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
        
        if game_state.current_combat:
            game_state.current_combat.remove_enemy(self.enemy)
        
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
        
        if game_state.current_combat:
            game_state.current_combat.add_enemy(self.enemy)
        
        return NoneResult()

@register("action")
class HealAction(Action):
    """Heal the player for a specified amount

    Required:
        amount (int): Amount to heal

    Optional:
        None
    """
    # todo: new parameter: target
    # reason: enemky can also heal
    def __init__(self, amount: int):
        self.amount = amount

    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state
        actions_to_return = []
        
        if game_state.player:
            # Trigger on_heal hook
            actions = game_state.player.on_heal(self.amount)
            if actions:
                actions_to_return.extend(actions)

            # Trigger relic on_heal hooks
            for relic in game_state.player.relics:
                if hasattr(relic, "on_heal"):
                    relic_actions = relic.on_heal(
                        heal_amount=self.amount,
                        player=game_state.player,
                        entities=game_state.current_combat.enemies if game_state.current_combat else [],
                    )
                    if relic_actions:
                        actions_to_return.extend(relic_actions)

            # Actually heal (only numerical changes)
            old_hp = game_state.player.hp
            game_state.player.hp = min(game_state.player.hp + self.amount, game_state.player.max_hp)
            healed = game_state.player.hp - old_hp
            print(t("ui.healed", default=f"Healed for {healed} HP.", amount=healed))
        
        if actions_to_return:
            return MultipleActionsResult(actions_to_return)
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
        actions_to_return = []
        
        if game_state.player:
            # Trigger on_lose_hp hook
            actions = game_state.player.on_lose_hp(self.amount)
            if actions:
                actions_to_return.extend(actions)

            # Actually lose HP (only numerical changes)
            old_hp = game_state.player.hp
            game_state.player.hp -= self.amount
            lost = old_hp - game_state.player.hp
            print(t("ui.lost_hp", default=f"Lost {lost} HP.", amount=lost))
        
        if actions_to_return:
            return MultipleActionsResult(actions_to_return)
        return NoneResult()

# todo: 和block进行交互
@register("action")
class DealDamageAction(Action):
    """Deal damage to a target (basic damage action)

    This action performs the core damage operation:
    - Calculate damage value (handles callable)
    - Trigger creature hooks (on_damage_dealt, on_damage_taken)
    - Trigger relic hooks (on_damage_dealt)
    - Reduce target HP (via Creature.take_damage)

    Complex damage modifiers (strength, weak, vulnerable, artifact, etc.)
    should be handled by AttackAction or similar higher-level actions.

    Required:
        damage (int): Damage amount to deal
        target (Creature): Target creature
        damage_type (str): Type of damage ("direct", "attack", etc.)

    Optional:
        card (Card): Card that caused the damage (for power triggers)
        source (Any): Source of the damage. It may be even relic or power.
    """
    def __init__(self, damage: int, target: Creature,
                 damage_type: str = "direct", card=None, source=None):
        self.damage = damage
        self.target = target
        self.damage_type = damage_type
        self.card = card
        self.source = source

    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state
        actions_to_return = []

        if not self.target or self.target.is_dead():
            return NoneResult()

        # Get base damage
        damage_amount = self.damage
        
        # Defensive fix: handle case where damage is accidentally a list
        if isinstance(damage_amount, list):
            print(f"[DEBUG] Converting damage list to int: {damage_amount} -> {damage_amount[0] if damage_amount else 0}")
            damage_amount = damage_amount[0] if damage_amount else 0

        # Apply attacker's damage modifiers (Strength, Weakness)
        if self.source and hasattr(self.source, 'get_damage_dealt_modifier'):
            damage_amount = self.source.get_damage_dealt_modifier(damage_amount)
        
        # Apply defender's damage taken multiplier (Vulnerable, Buffer)
        if hasattr(self.target, 'get_damage_taken_multiplier'):
            multiplier = self.target.get_damage_taken_multiplier()
            damage_amount = int(damage_amount * multiplier)

        # Check for BufferPower damage prevention
        if hasattr(self.target, 'try_prevent_damage') and self.target.try_prevent_damage():
            from localization import t
            target_name = getattr(self.target, 'name', getattr(self.target, 'character', 'Unknown'))
            print(t("combat.buffer_prevented", default="{target_name}'s Buffer prevented the damage!", target_name=target_name))
            return NoneResult()

        # Actually deal damage (Creature.take_damage only handles numerical changes)
        damage_dealt = self.target.take_damage(
            damage_amount,
            source=self.source,
            card=self.card,
            damage_type=self.damage_type
        )

        # Trigger target's on_damage_taken hook
        target_actions = self.target.on_damage_taken(
            damage_dealt,
            source=self.source,
            card=self.card,
            damage_type=self.damage_type
        )
        if target_actions:
            actions_to_return.extend(target_actions)
        
        # Print damage dealt
        from localization import t, LocalStr
        target_name = getattr(self.target, 'name', None)
        if target_name is None:
            target_name = getattr(self.target, 'character', 'Unknown')
        # Resolve LocalStr if needed
        if isinstance(target_name, LocalStr):
            target_name = target_name.resolve()
        print(t("combat.deal_damage_enemy", default="Deal {amount} damage to {target_name}!", amount=damage_dealt, target_name=target_name))

        # Trigger source's on_damage_dealt hook before dealing damage
        if self.source:
            source_actions = self.source.on_damage_dealt(
                damage_dealt,
                target=self.target,
                card=self.card,
                damage_type=self.damage_type
            )
            if source_actions:
                actions_to_return.extend(source_actions)
        
        # Trigger card's on_damage_dealt
        if self.card and hasattr(self.card, 'on_damage_dealt'):
            card_actions = self.card.on_damage_dealt(
                damage_dealt,
                target=self.target,
                card=self.card,
                damage_type=self.damage_type
            )
            if card_actions:
                actions_to_return.extend(card_actions)
                
        # Trigger on_fatal - check if target is an enemy by checking for is_intention attribute
        if hasattr(self.target, 'is_intention') and self.target.is_dead():
            if self.card is not None:
                actions_to_return.extend(self.card.on_fatal())

        # Trigger relic hooks (on_damage_dealt)
        for relic in game_state.player.relics:
            if hasattr(relic, "on_damage_dealt"):
                actions = relic.on_damage_dealt(
                    damage=damage_dealt,
                    target=self.target,
                    player=game_state.player,
                    entities=game_state.current_combat.enemies if game_state.current_combat else [],
                )
                if actions:
                    actions_to_return.extend(actions)

        # Check if target died from this damage and return death actions
        if self.target.is_dead():
            death_actions = self.target.on_death()
            if death_actions:
                actions_to_return.extend(death_actions)

        if actions_to_return:
            return MultipleActionsResult(actions_to_return)
        return NoneResult()
    
@register("action")
class AttackAction(Action):
    """Attack the enemy.
    
    和DealDamageAction不同，AttackAction封装了动态计算攻击力的逻辑。
    
    Required:
        damage (int or callable): Damage amount to deal
        target (Creature): Target creature
        source (Creature): Source of the damage
        damage_type (str): Type of damage ("direct", "attack", etc.)

    Optional:
        card (Card): Card that caused the damage (for power triggers)  
    """
    
    def __init__(self, damage: int, 
                 target: Creature, source: Creature,
                 damage_type: str = "direct", card=None):
        self.damage = damage
        self.target = target
        self.damage_type = damage_type
        self.card = card
        self.source = source
        
    def execute(self) -> 'BaseResult':
        from utils.dynamic_values import resolve_potential_damage
        damage = resolve_potential_damage(self.damage, self.source, self.target)
        return SingleActionResult(DealDamageAction(damage, 
                                    target=self.target, 
                                    damage_type=self.damage_type,
                                    card=self.card,
                                    source=self.source))

@register("action")
class GainBlockAction(Action):
    """Gain block for a creature

    Required:
        block (int or callable): Block amount to gain
        target (Creature): Target to gain block (defaults to player)
    """
    def __init__(self, block, target: Creature, source=None, card=None):
        self.block = block
        self.target = target
        self.source = source
        self.card = card

    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state
        actions_to_return = []

        # Resolve callable block values first
        block_amount = self.block() if callable(self.block) else self.block

        # Trigger target's on_gain_block hook
        if self.target:
            actions = self.target.on_gain_block(
                block_amount,
                source=self.source,
                card=self.card
            )
            if actions:
                actions_to_return.extend(actions)

        # Trigger power hooks for on_gain_block (pass resolved int amount)
        for power in list(self.target.powers):
            if hasattr(power, "on_gain_block"):
                power_actions = power.on_gain_block(
                    block_amount,
                    player=self.target,
                    source=self.source,
                    card=self.card
                )
                if power_actions:
                    actions_to_return.extend(power_actions)

        # Actually gain block (Creature.gain_block only handles numerical changes)
        self.target.gain_block(block_amount, source=self.source, card=self.card)
        
        # Print block gained for player feedback
        target_name = getattr(self.target, 'name', getattr(self.target, 'character', 'Creature'))
        print(t('combat.gain_block').format(name=target_name, amount=block_amount))

        if actions_to_return:
            return MultipleActionsResult(actions_to_return)
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
            # Print energy change for player feedback
            if self.energy != 0:
                print(t('combat.gain_energy').format(amount=self.energy))
            
        return NoneResult()

@register("action")
class PlayCardAction(Action):
    """Play a card

    Required:
        card (Card): Card to play
        is_auto (bool): whether auto playing the card without choosing target
        ignore_energy (bool): whether player the card without consuming energy

    Optional:
        None
    """
    if TYPE_CHECKING:
        from cards.base import Card
    def __init__(self, card: 'Card', is_auto: bool = False, ignore_energy: bool = False): 
        self.card = card
        self.is_auto = is_auto
        self.ignore_energy = ignore_energy

    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state
        player = game_state.player
        enemies = game_state.current_combat.enemies

        if not self.card:
            return NoneResult()

        # Check if card can be played
        can_play, reason = self.card.can_play(self.ignore_energy)
        if not can_play:
            print(f"Cannot play card: {reason}")
            return SingleActionResult(DiscardCardAction(card=self.card))
        
        # determine target
        from utils.types import CardType
        if self.card.card_type != CardType.ATTACK:
            target = player
            return SingleActionResult(PlayCardBHAction(card=self.card, target=target, ignore_energy=self.ignore_energy))
        else:
            if self.is_auto:
                from utils.combat import resolve_target
                target_type = self.card.target_type
                assert target_type is not None
                target = resolve_target(target_type)
                return SingleActionResult(PlayCardBHAction(card=self.card, target=target, ignore_energy=self.ignore_energy))
            else:
                from utils.option import Option
                from localization import LocalStr
                options = []
                for enemy in enemies:
                    options.append(Option(
                        name=LocalStr("ui.select_enemy"),
                        actions=[PlayCardBHAction(card=self.card, target=enemy, ignore_energy=self.ignore_energy)]
                    ))
                
        return NoneResult()
    
        
    
@register("action")
class PlayCardBHAction(Action):
    """
    Finish playing card
    
    Required:
        card (Card): Card to play
        target (Creature): card's target
        ignore_energy (bool): whether player the card without consuming energy

    Optional:
        None
    """    
    
    if TYPE_CHECKING:
        from cards.base import Card
        from entities.creature import Creature
    def __init__(self, card: 'Card', target: 'Creature', ignore_energy: bool = False):
        self.card = card
        self.target = target
        self.ignore_energy = ignore_energy
        
    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state
        player = game_state.player
        enemies = game_state.current_combat.enemies
        
        # Spend energy
        cost = self.card.cost
        if cost > 0 and not self.ignore_energy:
            game_state.player.gain_energy(-cost)
            game_state.current_combat.combat_state.player_energy_spent_this_turn += cost
        
        actions = []
        # 1. Trigger card's on_play
        actions.extend(self.card.on_play(target=self.target))
        
        # 2. Trigger powers
        for power in player.powers:
            if hasattr(power, 'on_play_card'):
                actions.extend(power.on_play_card())
        for enemy in enemies:
            for power in enemy.powers:
                if hasattr(power, 'on_play_card'):
                    actions.extend(power.on_play_card())
        
        # 3. Trigger relics
        for relic in player.relics:
            if hasattr(relic, 'on_play_card'):
                actions.extend(relic.on_play_card())

        # Update turn tracking
        game_state.current_combat.combat_state.turn_cards_played += 1
        game_state.current_combat.combat_state.player_actions_this_turn += 1
        
        # Print card played for player feedback
        from localization import t
        card_name = self.card.display_name.resolve() if hasattr(self.card, 'display_name') else str(self.card)
        print(t('combat.play_card').format(card=card_name))

        # Remove card from hand
        from actions.card import ExhaustCardAction
        if self.card.get_value('exhaust'):
            actions.append(ExhaustCardAction(card=self.card))
        else:
            # Move to discard pile
            actions.append(DiscardCardAction(card=self.card))

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
        game_state.current_combat.combat_state.current_phase = "enemy_action"
        
        # Print turn ended for player feedback
        print(t('combat.end_turn'))

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
        from engine.game_state import game_state
        
        if not self.target:
            return NoneResult()

        # If power is a string, get the registered power class
        if isinstance(self.power, str):
            # Try exact name first, then with "Power" suffix
            power_class = get_registered("power", self.power)
            if not power_class:
                # Try with "Power" suffix (e.g., "Vulnerable" -> "VulnerablePower")
                power_class = get_registered("power", f"{self.power}Power")
            if not power_class:
                # Try capitalizing first letter
                power_class = get_registered("power", self.power.capitalize())
                if not power_class:
                    power_class = get_registered("power", f"{self.power.capitalize()}Power")
            if not power_class:
                print(f"Power {self.power} not found")
                return NoneResult()
            power_instance = power_class(amount=self.amount, duration=self.duration)
        else:
            # Already a Power instance
            power_instance = self.power

        # Trigger on_power_added hook before adding
        actions = self.target.on_power_added(power_instance)

        # Apply the power to the target (only numerical changes)
        self.target.add_power(power_instance)
        
        if actions:
            return MultipleActionsResult(actions)
        return NoneResult()

@register("action")
class RemovePowerAction(Action):
    """Remove a power from a target creature

    Required:
        power (str): Power name string to remove
        target (Creature): Target creature to remove power from

    Optional:
        is_buff (bool): Whether to filter by buff/debuff type (True=buff, False=debuff, None=any)
    """
    def __init__(self, power: str, target: Creature, is_buff: Optional[bool] = None):
        self.power = power
        self.target = target
        self.is_buff = is_buff

    def execute(self) -> 'BaseResult':
        """Remove the power from the target creature"""
        from engine.game_state import game_state
        
        if not self.target:
            return NoneResult()

        # If is_buff is specified, check if power matches the type before removing
        if self.is_buff is not None:
            power_to_remove = self.target.get_power(self.power)
            if power_to_remove and power_to_remove.is_buff != self.is_buff:
                # Power type doesn't match, don't remove
                return NoneResult()

        # Remove the power (only numerical changes)
        self.target.remove_power(self.power)
        
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

