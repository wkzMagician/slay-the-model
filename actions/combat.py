from actions.base import Action
from typing import Optional, Callable, Any, List, TYPE_CHECKING
from actions.card import DiscardCardAction
from utils.result_types import BaseResult, BaseResult, NoneResult, SingleActionResult, MultipleActionsResult
from localization import t
from utils.registry import register
from entities.creature import Creature
from utils.types import TargetType

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
    """Heal a creature for a specified amount or percentage

    Required (one of):
        amount (int): Amount to heal
        percent (float): Percentage of max_hp to heal (0.0-1.0)

    Optional:
        target (Creature): Target to heal (defaults to player)
    """
    def __init__(self, amount: int | None = None, percent: float | None = None, target: 'Creature' = None):
        self.amount = amount
        self.percent = percent
        self.target = target

    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state
        actions_to_return = []

        # Default to player if no target specified
        heal_target = self.target if self.target else game_state.player

        if heal_target:
            # Calculate heal amount
            if self.percent is not None:
                heal_amount = int(heal_target.max_hp * self.percent)
            else:
                heal_amount = self.amount() if callable(self.amount) else (
                    self.amount or 0
                )

            # Trigger on_heal hook
            actions = heal_target.on_heal(heal_amount)
            if actions:
                actions_to_return.extend(actions)

            # Trigger relic on_heal hooks (only for player)
            if heal_target == game_state.player:
                for relic in game_state.player.relics:
                    if hasattr(relic, "on_heal"):
                        relic_actions = relic.on_heal(
                            heal_amount=heal_amount,
                            player=game_state.player,
                            entities=game_state.current_combat.enemies if game_state.current_combat else [],
                        )
                        if relic_actions:
                            actions_to_return.extend(relic_actions)

            # Actually heal (only numerical changes)
            old_hp = heal_target.hp
            heal_target.hp = min(heal_target.hp + heal_amount, heal_target.max_hp)
            healed = heal_target.hp - old_hp
            print(t("ui.healed", default=f"Healed for {healed} HP.", amount=healed))

        if actions_to_return:
            return MultipleActionsResult(actions_to_return)
        return NoneResult()

@register("action")
class LoseHPAction(Action):
    """Make a creature lose HP (not damage, bypasses block)

    Required (one of):
        amount (int): Amount of HP to lose
        percent (float): Percentage of max_hp to lose (0.0-1.0)

    Optional:
        target (Creature): Target to lose HP (defaults to player)
    """
    def __init__(self, amount: int | None = None, percent: float | None = None, target: 'Creature' = None):
        self.amount = amount
        self.percent = percent
        self.target = target

    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state
        actions_to_return = []

        # Default to player if no target specified
        lose_target = self.target if self.target else game_state.player

        if lose_target:
            # Calculate HP loss amount (handles callable)
            if self.percent is not None:
                hp_loss = int(lose_target.max_hp * self.percent)
            else:
                hp_loss = self.amount() if callable(self.amount) else (self.amount or 0)

            # Check for damage prevention (e.g., BufferPower)
            if lose_target.try_prevent_damage(hp_loss):
                print(t("ui.hp_loss_prevented", default=f"HP loss prevented.", amount=hp_loss))
                return NoneResult()

            # Trigger on_lose_hp hook
            actions = lose_target.on_lose_hp(hp_loss)
            if actions:
                actions_to_return.extend(actions)

            # Actually lose HP (only numerical changes)
            old_hp = lose_target.hp
            lose_target.hp -= hp_loss
            lost = old_hp - lose_target.hp
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
        from utils.dynamic_values import resolve_potential_damage
        actions_to_return = []

        if not self.target or self.target.is_dead():
            return NoneResult()

        # ====================
        # DAMAGE CALCULATION (Single Point of Truth)
        # ====================
        # If source is provided, use unified damage pipeline
        # This ensures all modifiers (Strength, Weak, Vulnerable, Intangible, etc.)
        # are applied exactly once in the correct order.
        if self.source is not None:
            damage_amount = resolve_potential_damage(
                self.damage, 
                self.source, 
                self.target, 
                card=self.card
            )
        else:
            # Fallback for damage without source (relics, powers, etc.)
            damage_amount = self.damage
            if callable(damage_amount):
                damage_amount = damage_amount()
            if isinstance(damage_amount, list):
                damage_amount = damage_amount[0] if damage_amount else 0

        # ====================
        # DAMAGE PREVENTION (Buffer)
        # ====================
        # Check for BufferPower damage prevention - this is separate from modifiers
        if hasattr(self.target, 'try_prevent_damage') and self.target.try_prevent_damage(damage_amount):
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

        # Trigger target's on_damage_taken hook.
        # Keep backward compatibility with older enemy signatures.
        if damage_dealt > 0:
            try:
                target_actions = self.target.on_damage_taken(
                    damage_dealt,
                    source=self.source,
                    card=self.card,
                    damage_type=self.damage_type
                )
            except TypeError:
                try:
                    target_actions = self.target.on_damage_taken(
                        damage_dealt,
                        source=self.source
                    )
                except TypeError:
                    target_actions = self.target.on_damage_taken(damage_dealt)
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
            # Print enemy kill notification
            from enemies.base import Enemy
            if isinstance(self.target, Enemy):
                print(t("combat.enemy_killed", default="Enemy {target_name} has been defeated!", target_name=target_name))

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
        # NOTE: Do NOT pre-resolve damage here!
        # DealDamageAction will call resolve_potential_damage itself.
        # Pre-resolving would cause double modifier application.
        
        actions_to_return = []
        
        # Trigger on_attack hooks for source's powers (e.g., ThieveryPower)
        # This is called before damage is dealt, allowing effects that trigger on attack
        if self.source and hasattr(self.source, 'powers'):
            for power in self.source.powers:
                if hasattr(power, 'on_attack'):
                    power_actions = power.on_attack(
                        target=self.target,
                        source=self.source,
                        card=self.card
                    )
                    if power_actions:
                        actions_to_return.extend(power_actions)
        
        # Create DealDamageAction with RAW damage - it will resolve internally
        damage_action = DealDamageAction(self.damage, 
                                    target=self.target, 
                                    damage_type=self.damage_type,
                                    card=self.card,
                                    source=self.source)
        
        # Return damage action along with any actions from on_attack hooks
        if actions_to_return:
            actions_to_return.append(damage_action)
            return MultipleActionsResult(actions_to_return)
        return SingleActionResult(damage_action)

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
        print(t('combat.gain_block').format(source=target_name, amount=block_amount))

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
            # Handle callable energy amount
            energy_amount = self.energy() if callable(self.energy) else self.energy
            game_state.player.gain_energy(energy_amount)
            # Print energy change for player feedback
            if energy_amount != 0:
                print(t('combat.gain_energy').format(amount=energy_amount))
            
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
        from utils.combat import resolve_target
        from utils.types import CardType
        from utils.option import Option
        from localization import LocalStr
        from actions.display import SelectAction
        
        if not self.card:
            return NoneResult()

        # Check if card can be played
        can_play, reason = self.card.can_play(self.ignore_energy)
        if not can_play:
            print(f"Cannot play card: {reason}")
            return NoneResult()
        
        if self.card.target_type == TargetType.ENEMY_SELECT and self.is_auto:
            targets = resolve_target(TargetType.ENEMY_RANDOM)
            return SingleActionResult(PlayCardBHAction(card=self.card, targets=targets, ignore_energy=self.ignore_energy))
        else:
            assert self.card.target_type is not None
            targets = resolve_target(self.card.target_type)
            return SingleActionResult(PlayCardBHAction(card=self.card, targets=targets, ignore_energy=self.ignore_energy))
     
    
@register("action")
class PlayCardBHAction(Action):
    """
    Finish playing card
    
    Required:
        card (Card): Card to play
        targets (List[Optional[Creature]]): card's target
        ignore_energy (bool): whether player the card without consuming energy

    Optional:
        None
    """    
    
    if TYPE_CHECKING:
        from cards.base import Card
        from entities.creature import Creature
    def __init__(self, card: 'Card', targets: List[Optional['Creature']], ignore_energy: bool = False):
        self.card = card
        self.targets = targets
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
        
        # BackAttack transfer: if single-target enemy, trigger transfer
        if self.targets and len(self.targets) == 1:
            target = self.targets[0]
            from enemies.base import Enemy
            if isinstance(target, Enemy):
                from engine.back_attack_manager import BackAttackManager
                manager = BackAttackManager()
                manager.maybe_transfer_on_target(target)
        
        # 1. Trigger card's on_play
        actions.extend(self.card.on_play(targets=self.targets))
        
        # 2. Trigger powers
        for power in player.powers:
            if hasattr(power, 'on_play_card'):
                actions.extend(power.on_play_card())
        for enemy in enemies:
            for power in enemy.powers:
                # Check both on_play_card and on_card_play hooks
                if hasattr(power, 'on_play_card'):
                    actions.extend(power.on_play_card())
                if hasattr(power, 'on_card_play'):
                    actions.extend(power.on_card_play(self.card, player, enemies))
        
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
        if self.card.get_value('exhaust') == True:
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
        duration (int): Power duration (None to use power's default, 0 for permanent)
    """
    def __init__(self, power, target: Creature, amount: int, duration: int = None):
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
            # Create power instance - only pass duration if specified, let power use its default otherwise
            if self.duration is not None:
                power_instance = power_class(amount=self.amount, duration=self.duration)
            else:
                power_instance = power_class(amount=self.amount)
        else:
            # Already a Power instance
            power_instance = self.power

        # Trigger on_power_added hook before adding
        actions = self.target.on_power_added(power_instance)

        # Check if this is a debuff and target has Artifact to block it
        if not getattr(power_instance, 'is_buff', True):
            if self.target.try_prevent_debuff():
                print(f"[Artifact] {self.target} blocked {power_instance.name}!")
                return NoneResult()

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


@register("action")
class StartFightAction(Action):
    """Start a fight with specified enemies
    
    Required:
        enemies (list): List of enemy names or IDs to fight
    
    Optional:
        None
    """
    def __init__(self, enemies: list):
        self.enemies = enemies
    
    def execute(self) -> 'BaseResult':
        """Start combat with the specified enemies"""
        from engine.game_state import game_state
        from engine.combat import Combat
        
        # Create enemy instances from names
        enemy_instances = []
        for enemy_name in self.enemies:
            if enemy_name == 'random_act1_boss':
                # Special case: random Act 1 boss
                import random
                from utils.registry import get_registered
                bosses = ['slime_boss', 'hexaghost', 'the_guardian']
                enemy_name = random.choice(bosses)
            
            from utils.registry import get_registered
            enemy_class = get_registered("enemy", enemy_name)
            if enemy_class:
                enemy_instances.append(enemy_class())
        
        if not enemy_instances:
            return NoneResult()
        
        # Start combat
        combat = Combat(game_state.player, enemy_instances)
        game_state.current_combat = combat
        
        return NoneResult()

@register("action")
class LoseMaxHPAction(Action):
    """Lose max HP permanently
    
    Required:
        amount (int): Amount of max HP to lose
    
    Optional:
        None
    """
    def __init__(self, amount: int):
        self.amount = amount
    
    def execute(self) -> 'BaseResult':
        """Reduce player's max HP"""
        from engine.game_state import game_state
        
        player = game_state.player
        player.max_hp -= self.amount
        player.hp = min(player.hp, player.max_hp)
        
        print(f"Lost {self.amount} max HP. New max HP: {player.max_hp}")
        return NoneResult()

@register("action")
class UsePotionAction(Action):
    """Action to use a potion on a target"""
    
    def __init__(self, potion, target=None):
        self.potion = potion
        self.target = target
    
    def execute(self) -> 'BaseResult':
        """Execute potion effect with dynamic target selection and BackAttack transfer."""
        from engine.game_state import game_state
        from utils.result_types import MultipleActionsResult
        from actions.display import SelectAction, Option
        
        # Dynamic target selection for combat situations
        if self.target is None:
            self.target = game_state.player
        
        # If in combat with multiple enemies, allow targeting selection
        if (hasattr(game_state, 'current_combat') and 
            game_state.current_combat is not None):
            
            alive_enemies = [e for e in game_state.current_combat.enemies if e.is_alive]
            
            if len(alive_enemies) > 1:
                # Create options for each enemy + player
                from localization import LocalStr
                options = []
                
                # Add player option
                player_name = getattr(game_state.player, 'name', 'Player')
                options.append(Option(
                    name=LocalStr(f"[{player_name}]"),
                    actions=[UsePotionAction(potion=self.potion, target=game_state.player)]
                ))
                
                # Add enemy options
                for enemy in alive_enemies:
                    enemy_name = getattr(enemy, 'name', 'Enemy')
                    options.append(Option(
                        name=LocalStr(f"[Enemy] {enemy_name}"),
                        actions=[UsePotionAction(potion=self.potion, target=enemy)]
                    ))
                
                return SelectAction(
                    options=options,
                    prompt=LocalStr("Select potion target")
                )
        
        # Now self.target is determined - check BackAttack transfer
        from engine.back_attack_manager import BackAttackManager
        manager = BackAttackManager()
        
        # If targeting an enemy (not player), check for BackAttack transfer
        if (self.target != game_state.player and 
            hasattr(self.target, 'has_power') and 
            self.target.has_power("Back Attack")):
            manager.maybe_transfer_on_target(self.target)
        
        # Get actions from potion's on_use method
        actions = self.potion.on_use(self.target)
        
        # Remove potion from player's inventory
        if self.potion in game_state.player.potions:
            game_state.player.potions.remove(self.potion)
        
        target_name = getattr(self.target, 'name', str(self.target))
        print(f"Used potion: {self.potion.name} on {target_name}")
        
        return MultipleActionsResult(actions)
        return NoneResult()
