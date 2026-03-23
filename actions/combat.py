from actions.base import Action
from typing import Optional, Callable, Any, List, TYPE_CHECKING
from utils.result_types import BaseResult, BaseResult, NoneResult, SingleActionResult, MultipleActionsResult
from localization import t
from utils.registry import register
from entities.creature import Creature

# Helper function to localize character names
def _localize_character_name(raw_name: str) -> str:
    """Convert English character name to localized version."""
    if raw_name in ('Ironclad', 'Silent', 'Defect', 'Watcher'):
        return t(f'ui.character.{raw_name.lower()}', default=raw_name)
    return raw_name
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
        from enemies.base import Enemy
        
        if game_state.current_combat:
            enemy = self.enemy() if isinstance(self.enemy, type) else self.enemy
            if isinstance(enemy, Enemy):
                game_state.current_combat.add_enemy(enemy)
        
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

            # Apply healing modifiers from relics/powers.
            if heal_target == game_state.player:
                for relic in list(game_state.player.relics):
                    if hasattr(relic, "modify_heal"):
                        heal_amount = relic.modify_heal(heal_amount)
            if hasattr(heal_target, "powers"):
                for power in list(heal_target.powers):
                    if hasattr(power, "modify_heal"):
                        heal_amount = power.modify_heal(heal_amount)
            heal_amount = max(0, int(heal_amount))

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
        card (Card): Card that caused the HP loss (for Rupture triggers)
        source (Any): Source of the HP loss
    """
    def __init__(self, amount: int | None = None, percent: float | None = None, 
                 target: 'Creature' = None, card=None, source=None):
        self.amount = amount
        self.percent = percent
        self.target = target
        self.card = card
        self.source = source

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

            # Trigger on_lose_hp hook with card and source info
            actions = lose_target.on_lose_hp(hp_loss, source=self.source, card=self.card)
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
            target_name = _localize_character_name(target_name)
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
        # Localize character name
        target_name = _localize_character_name(target_name)
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
                
        # Trigger on_fatal - check if target is an enemy and NOT a minion
        # Minions (summoned enemies) should not trigger on_fatal effects
        from enemies.base import Enemy
        if isinstance(self.target, Enemy) and self.target.is_dead():
            if not self.target.is_minion:
                if self.card is not None and hasattr(self.card, 'on_fatal'):
                    actions_to_return.extend(self.card.on_fatal())
            # Print enemy kill notification (for all enemies including minions)
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
    def __init__(self, block=None, target: Creature = None, source=None, card=None, amount=None):
        if block is None:
            block = amount
        if block is None:
            raise ValueError("GainBlockAction requires 'block' or legacy 'amount'")
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
        target_name = _localize_character_name(target_name)
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
        from localization import LocalStr
        from actions.display import InputRequestAction
        from utils.option import Option
        
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
            if self.card.target_type == TargetType.ENEMY_SELECT and len(targets) > 1:
                options = []
                for enemy in targets:
                    options.append(
                        Option(
                            name=LocalStr(
                                "combat.select_enemy_option",
                                default=f"{enemy.name} (HP: {enemy.hp}/{enemy.max_hp})",
                            ),
                            actions=[
                                PlayCardBHAction(
                                    card=self.card,
                                    targets=[enemy],
                                    ignore_energy=self.ignore_energy,
                                )
                            ],
                        )
                    )
                return SingleActionResult(
                    InputRequestAction(
                        title=LocalStr("combat.select_target", default="Select Target"),
                        options=options,
                    )
                )
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
        from cards.base import COST_X
        from utils.types import CardType
        player = game_state.player
        enemies = game_state.current_combat.enemies
        
        # Spend energy
        cost = self.card.cost
        if getattr(self.card, "_cost", None) == COST_X:
            cost = player.energy
            self.card._x_cost_energy = cost
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
        print(t('combat.play_card', card=card_name))

        # Remove card from hand
        from actions.card import DiscardCardAction, ExhaustCardAction
        has_medical_kit = any(
            getattr(relic, "idstr", None) == "MedicalKit"
            for relic in player.relics
        )
        should_exhaust_status = (
            has_medical_kit and self.card.card_type == CardType.STATUS
        )
        has_blue_candle = any(
            getattr(relic, "idstr", None) == "BlueCandle"
            for relic in player.relics
        )
        should_exhaust_curse = (
            has_blue_candle and self.card.card_type == CardType.CURSE
        )
        will_exhaust = (
            self.card.get_value('exhaust') is True
            or should_exhaust_status
            or should_exhaust_curse
        )

        prevent_exhaust = False
        if will_exhaust:
            for relic in player.relics:
                hook = getattr(relic, "should_prevent_exhaust", None)
                if not hook:
                    continue
                if hook(card=self.card):
                    prevent_exhaust = True
                    break

        is_power_card = self.card.card_type == CardType.POWER

        if will_exhaust and prevent_exhaust:
            actions.append(DiscardCardAction(card=self.card))
        elif will_exhaust:
            actions.append(ExhaustCardAction(card=self.card))
        else:
            if is_power_card:
                # Normal Power cards should leave the hand and not go to discard or exhaust.
                # Remove the card instance from hand without adding it to any pile.
                from player.card_manager import CardManager  # type: ignore  # for static checkers
                player.card_manager.remove_from_pile(self.card, 'hand')
            else:
                # Default: move non-Power cards to discard pile
                actions.append(DiscardCardAction(card=self.card))

        if should_exhaust_curse:
            hp_loss = 1
            for relic in player.relics:
                if getattr(relic, "idstr", None) == "BlueCandle":
                    hook = getattr(relic, "curse_play_hp_loss", None)
                    if hook:
                        hp_loss = hook()
                    break
            actions.append(LoseHPAction(amount=hp_loss, target=player, source=self.card))

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

        # Transition to the explicit player-end phase.
        game_state.current_combat.combat_state.current_phase = "player_end"
        
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
        duration (int): Power duration (None to use power's default, 0 for permanent)
        amount (int): Power amount        
        
    """
    def __init__(self, power, target: Creature, duration: int = -1, amount: int = 0):
        self.power = power
        self.target = target
        self.duration = duration
        self.amount = amount

    def execute(self) -> 'BaseResult':
        """Apply the power to the target creature"""
        from utils.registry import get_registered
        from engine.game_state import game_state
        from powers.base import Power
        
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
                raise ValueError(f"Power {self.power} not found")
            # Create power instance
            power_instance = power_class(amount=self.amount, duration=self.duration)
        elif isinstance(self.power, type) and issubclass(self.power, Power):
            power_instance = self.power(amount=self.amount, duration=self.duration)
        else:
            # Already a Power instance
            power_instance = self.power

        # Check if target's relics prevent this power (e.g., Ginger prevents Weak, Turnip prevents Frail)
        if game_state.player and self.target == game_state.player:
            power_name_lower = getattr(power_instance, 'idstr', '').lower()
            if not power_name_lower:
                power_name_lower = str(self.power).lower() if isinstance(self.power, str) else ''
            for relic in game_state.player.relics:
                if hasattr(relic, "can_receive_power"):
                    if not relic.can_receive_power(power_name_lower):
                        print(f"[{relic.__class__.__name__}] Prevented {power_name_lower} from being applied!")
                        return NoneResult()

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


from utils.types import CombatType

@register("action")
class StartFightAction(Action):
    """Start a fight with specified enemies
    
    Required:
        enemies (List[Enemy]): List of Enemy instances to fight
    
    Optional:
        combat_type (CombatType): Type of combat (Normal/Elite/Boss)
        victory_actions (List[Action]): Actions to execute after combat victory
    """
    def __init__(self, enemies: List['Enemy'], combat_type: CombatType = CombatType.NORMAL, 
                 victory_actions: List[Action] = None):
        self.enemies = enemies
        self.combat_type = combat_type
        self.victory_actions = victory_actions or []
    
    def execute(self) -> 'BaseResult':
        """Start combat with the specified enemies"""
        from engine.game_state import game_state
        from engine.combat import Combat
        
        if not self.enemies:
            return NoneResult()
        
        # Start combat with enemy instances directly
        combat = Combat(enemies=self.enemies, combat_type=self.combat_type)
        result = combat.start()
        
        # Handle combat result
        if result.state == "COMBAT_WIN":
            # Execute victory actions
            for action in self.victory_actions:
                game_state.action_queue.add_action(action)
            game_state.drive_actions()
            return NoneResult()
        elif result.state == "GAME_LOSE":
            return result
        elif result.state == "COMBAT_ESCAPE":
            # Player escaped, no victory rewards
            return NoneResult()
        
        return result

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
    """Resolve target and prepare potion usage.
    
    Required:
        potion (Potion): Potion to use
    
    Optional:
        target (Creature): Explicit target (skips target resolution)
    """
    
    def __init__(self, potion, target=None):
        self.potion = potion
        self.target = target
    
    def execute(self) -> 'BaseResult':
        """Resolve targets and delegate to UsePotionBHAction."""
        from utils.combat import resolve_target
        from actions.display import InputRequestAction
        from localization import LocalStr
        from utils.option import Option

        if self.target is not None:
            # Explicit single target provided
            targets = [self.target]
        else:
            # Resolve targets from potion's target_type
            targets = resolve_target(self.potion.target_type)

        if getattr(self.potion, "target_type", None) == TargetType.ENEMY_SELECT and len(targets) > 1:
            options = []
            for enemy in targets:
                options.append(
                    Option(
                        name=LocalStr(
                            "combat.select_enemy_option",
                            default=f"{enemy.name} (HP: {enemy.hp}/{enemy.max_hp})",
                        ),
                        actions=[UsePotionBHAction(potion=self.potion, targets=[enemy])],
                    )
                )
            return SingleActionResult(
                InputRequestAction(
                    title=LocalStr("combat.select_target", default="Select Target"),
                    options=options,
                )
            )
        
        return SingleActionResult(UsePotionBHAction(potion=self.potion, targets=targets))


@register("action")
class UsePotionBHAction(Action):
    """Execute potion effect on resolved targets.
    
    Required:
        potion (Potion): Potion to use
        targets (List[Creature]): Resolved target list
    """
    
    def __init__(self, potion, targets: List[Creature]):
        self.potion = potion
        self.targets = targets
    
    def execute(self) -> 'BaseResult':
        """Execute potion effect with BackAttack transfer and relic hooks."""
        from engine.game_state import game_state
        from localization import LocalStr
        
        # BackAttack transfer: check first enemy target
        if self.targets:
            from enemies.base import Enemy
            first_target = self.targets[0]
            if isinstance(first_target, Enemy):
                from engine.back_attack_manager import BackAttackManager
                manager = BackAttackManager()
                manager.maybe_transfer_on_target(first_target)
        
        # Get actions from potion's on_use method
        actions = self.potion.on_use(self.targets)

        # Trigger relic callbacks for potion use (e.g., ToyOrnithopter).
        relic_actions = []
        for relic in list(game_state.player.relics):
            if not hasattr(relic, "on_use_potion"):
                continue
            result = relic.on_use_potion(
                potion=self.potion,
                player=game_state.player,
                entities=game_state.current_combat.enemies if game_state.current_combat else [],
            )
            if result:
                relic_actions.extend(result if isinstance(result, list) else [result])

        # Remove potion from player's inventory
        if self.potion in game_state.player.potions:
            game_state.player.potions.remove(self.potion)
        
        # Print usage info
        target_names = []
        for target in self.targets:
            name = getattr(target, 'name', None) or getattr(target, 'character', 'Unknown')
            if isinstance(name, LocalStr):
                name = name.resolve()
            target_names.append(str(name))
        potion_name = self.potion.local("name").resolve() if isinstance(self.potion.local("name"), LocalStr) else self.potion.local("name")
        print(f"{t('combat.used_potion', default='Used potion')}: {potion_name} {t('combat.on_target', default='on')} {', '.join(target_names)}")

        all_actions = []
        if actions:
            all_actions.extend(actions if isinstance(actions, list) else [actions])
        all_actions.extend(relic_actions)

        return MultipleActionsResult(all_actions)
