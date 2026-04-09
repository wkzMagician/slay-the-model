from engine.runtime_api import add_action, add_actions, publish_message, request_input, set_terminal_state
from typing import List, Optional

from actions.base import Action
from entities.creature import Creature
from localization import LocalStr, t
from utils.registry import register
from utils.types import TargetType


@register("action")
class ApplyPowerAction(Action):
    """Apply a power to a target creature."""

    def __init__(self, power, target: Creature, duration: int = -1, amount: int = 0):
        self.power = power
        self.target = target
        self.duration = duration
        self.amount = amount

    def execute(self) -> None:
        from engine.game_state import game_state
        from engine.messages import PowerAppliedMessage
        from utils.registry import get_registered

        if not self.target:
            return

        if isinstance(self.power, str):
            power_class = get_registered("power", self.power)
            if not power_class:
                power_class = get_registered("power", f"{self.power}Power")
            if not power_class:
                power_class = get_registered("power", self.power.capitalize())
                if not power_class:
                    power_class = get_registered("power", f"{self.power.capitalize()}Power")
            if not power_class:
                raise ValueError(f"Power {self.power} not found")
            power_instance = power_class(amount=self.amount, duration=self.duration)
        elif isinstance(self.power, type):
            try:
                power_instance = self.power(amount=self.amount, duration=self.duration)
            except TypeError:
                power_instance = self.power(amount=self.amount, duration=self.duration, owner=self.target)
        else:
            power_instance = self.power

        if game_state.player and self.target == game_state.player:
            power_name_lower = getattr(power_instance, "idstr", "").lower()
            if not power_name_lower:
                power_name_lower = str(self.power).lower() if isinstance(self.power, str) else ""
            for relic in game_state.player.relics:
                can_receive_power = getattr(relic, "can_receive_power", None)
                if can_receive_power is not None and not can_receive_power(power_name_lower):
                    print(f"[{relic.__class__.__name__}] Prevented {power_name_lower} from being applied!")
                    return

        if not getattr(power_instance, "is_buff", True):
            if self.target.try_prevent_debuff():
                print(f"[Artifact] {self.target} blocked {power_instance.name}!")
                return

        self.target.add_power(power_instance)
        publish_message(
            PowerAppliedMessage(
                power=power_instance,
                target=self.target,
                owner=game_state.player,
                entities=game_state.current_combat.enemies if game_state.current_combat else [],
            ),
        )


@register("action")
class RemovePowerAction(Action):
    """Remove a power from a target creature."""

    def __init__(self, power: str, target: Creature, is_buff: Optional[bool] = None):
        self.power = power
        self.target = target
        self.is_buff = is_buff

    def execute(self) -> None:
        if not self.target:
            return

        if self.is_buff is not None:
            power_to_remove = self.target.get_power(self.power)
            if power_to_remove and power_to_remove.is_buff != self.is_buff:
                return

        self.target.remove_power(self.power)


@register("action")
class UsePotionAction(Action):
    """Resolve target and prepare potion usage."""

    def __init__(self, potion, target=None):
        self.potion = potion
        self.target = target

    def execute(self) -> None:
        from actions.display import InputRequestAction
        from engine.game_state import game_state
        from utils.combat import resolve_target
        from utils.option import Option

        if self.target is not None:
            targets = [self.target]
        else:
            targets = resolve_target(self.potion.target_type)

        if getattr(self.potion, "target_type", None) == TargetType.ENEMY_SELECT and len(targets) > 1:
            options = []
            for enemy in targets:
                if enemy is None:
                    continue
                enemy_name = getattr(enemy, "name", getattr(enemy, "character", "Unknown"))
                if isinstance(enemy_name, LocalStr):
                    enemy_name = enemy_name.resolve()
                options.append(
                    Option(
                        name=LocalStr(
                            "combat.select_enemy_option",
                            default=f"{enemy_name} (HP: {enemy.hp}/{enemy.max_hp})",
                        ),
                        actions=[UsePotionBHAction(potion=self.potion, targets=[enemy])],
                    )
                )
            add_action(
                InputRequestAction(
                    title=LocalStr("combat.select_target", default="Select Target"),
                    options=options,
                ),
                to_front=True,
            )
            return

        add_action(UsePotionBHAction(potion=self.potion, targets=targets), to_front=True)


@register("action")
class UsePotionBHAction(Action):
    """Execute potion effect on resolved targets."""

    def __init__(self, potion, targets: List[Creature]):
        self.potion = potion
        self.targets = targets

    def execute(self) -> None:
        from engine.game_state import game_state
        from engine.messages import PotionUsedMessage

        if not self.potion.can_use(self.targets):
            return

        if self.targets:
            from enemies.base import Enemy
            first_target = self.targets[0]
            if isinstance(first_target, Enemy):
                from engine.back_attack_manager import BackAttackManager
                manager = BackAttackManager()
                manager.maybe_transfer_on_target(first_target)

        self.potion.on_use(self.targets)

        if self.potion in game_state.player.potions:
            game_state.player.potions.remove(self.potion)

        target_names = []
        for target in self.targets:
            name = getattr(target, "name", None) or getattr(target, "character", "Unknown")
            if isinstance(name, LocalStr):
                name = name.resolve()
            target_names.append(str(name))
        potion_name = self.potion.local("name").resolve() if isinstance(self.potion.local("name"), LocalStr) else self.potion.local("name")
        print(f"{t('combat.used_potion', default='Used potion')}: {potion_name} {t('combat.on_target', default='on')} {', '.join(target_names)}")

        publish_message(
            PotionUsedMessage(
                potion=self.potion,
                owner=game_state.player,
                targets=self.targets,
                entities=game_state.current_combat.enemies if game_state.current_combat else [],
            )
        )
