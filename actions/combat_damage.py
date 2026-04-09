from engine.runtime_api import add_action, add_actions, publish_message, request_input, set_terminal_state
from collections.abc import Callable
from typing import TYPE_CHECKING, Any, cast

from actions.base import Action
from entities.creature import Creature
from localization import LocalStr, t
from utils.registry import register
from utils.types import DamageType
if TYPE_CHECKING:
    from enemies.base import Enemy


def _normalize_damage_type(damage_type: str | DamageType | None, *, direct: bool = False) -> DamageType:
    if direct:
        return DamageType.MAGICAL
    if isinstance(damage_type, DamageType):
        return damage_type
    if damage_type == "attack":
        return DamageType.PHYSICAL
    if damage_type == "hp_loss":
        return DamageType.HP_LOSS
    return DamageType.MAGICAL


def _apply_capping_damage_taken_modifiers(
    target: Creature | None,
    amount: int,
    source=None,
    damage_type: str | DamageType = DamageType.MAGICAL,
) -> int:
    """Apply only final capping hooks such as Intangible to HP loss."""
    from player.player import Player
    from utils.damage_phase import DamagePhase

    if target is None:
        return max(0, int(amount))

    damage = int(amount)
    if hasattr(target, "powers"):
        for power in target.powers:
            if getattr(power, "modify_phase", DamagePhase.ADDITIVE) == DamagePhase.CAPPING:
                modify_damage_taken = getattr(power, "modify_damage_taken", None)
                if callable(modify_damage_taken):
                    damage = cast(Any, modify_damage_taken)(damage)

    if isinstance(target, Player) and hasattr(target, "relics"):
        for relic in target.relics:
            if getattr(relic, "modify_phase", DamagePhase.ADDITIVE) == DamagePhase.CAPPING:
                modify_damage_taken = getattr(relic, "modify_damage_taken", None)
                if callable(modify_damage_taken):
                    damage = cast(Any, modify_damage_taken)(
                        damage,
                        source=source,
                        damage_type=damage_type,
                    )

    return max(0, int(damage))


def _localize_character_name(raw_name: str) -> str:
    """Convert English character name to localized version."""
    if raw_name in ("Ironclad", "Silent", "Defect", "Watcher"):
        return t(f"ui.character.{raw_name.lower()}", default=raw_name)
    return raw_name


@register("action")
class HealAction(Action):
    """Heal a creature for a specified amount or percentage."""

    def __init__(self, amount: int | None = None, percent: float | None = None, target: Creature | None = None):
        self.amount = amount
        self.percent = percent
        self.target = target

    def execute(self) -> None:
        from engine.game_state import game_state
        from engine.messages import HealedMessage

        heal_target = self.target if self.target else game_state.player

        if heal_target:
            if self.percent is not None:
                heal_amount = int(heal_target.max_hp * self.percent)
            else:
                heal_amount = self.amount() if callable(self.amount) else (self.amount or 0)

            if heal_target == game_state.player:
                for relic in list(game_state.player.relics):
                    modify_heal = getattr(relic, "modify_heal", None)
                    if modify_heal is not None:
                        heal_amount = modify_heal(heal_amount)
            if hasattr(heal_target, "powers"):
                for power in list(heal_target.powers):
                    if hasattr(power, "modify_heal"):
                        heal_amount = power.modify_heal(heal_amount)
            heal_amount = max(0, int(heal_amount))

            old_hp = heal_target.hp
            heal_target.hp = min(heal_target.hp + heal_amount, heal_target.max_hp)
            healed = heal_target.hp - old_hp
            print(t("ui.healed", default=f"Healed for {healed} HP.", amount=healed))
            publish_message(
                HealedMessage(
                    target=heal_target,
                    amount=healed,
                    previous_hp=old_hp,
                    new_hp=heal_target.hp,
                    source=self,
                )
            )


@register("action")
class LoseHPAction(Action):
    """Make a creature lose HP without interacting with block."""

    def __init__(self, amount: int | None = None, percent: float | None = None, target: Creature | None = None, card=None, source=None):
        self.amount = amount
        self.percent = percent
        self.target = target
        self.card = card
        self.source = source

    def execute(self) -> None:
        from engine.game_state import game_state
        from engine.messages import AnyHpLostMessage, DirectHpLossMessage, HpLostMessage

        lose_target = self.target if self.target else game_state.player

        if lose_target:
            if self.percent is not None:
                hp_loss = int(lose_target.max_hp * self.percent)
            else:
                hp_loss = self.amount() if callable(self.amount) else (self.amount or 0)

            hp_loss = _apply_capping_damage_taken_modifiers(
                lose_target,
                hp_loss,
                source=self.source,
                damage_type=DamageType.HP_LOSS,
            )

            if lose_target.try_prevent_damage(hp_loss):
                print(t("ui.hp_loss_prevented", default="HP loss prevented.", amount=hp_loss))
                return

            old_hp = lose_target.hp
            lose_target.hp -= hp_loss
            lost = old_hp - lose_target.hp
            print(t("ui.lost_hp", default=f"Lost {lost} HP.", amount=lost))
            publish_message(
                HpLostMessage(
                    target=lose_target,
                    amount=lost,
                    source=self.source,
                    card=self.card,
                )
            )
            publish_message(
                DirectHpLossMessage(
                    target=lose_target,
                    amount=lost,
                    source=self.source,
                    card=self.card,
                )
            )
            publish_message(
                AnyHpLostMessage(
                    target=lose_target,
                    amount=lost,
                    source=self.source,
                    card=self.card,
                )
            )


@register("action")
class DealDamageAction(Action):
    """Deal damage to a target creature."""

    def __init__(self, damage: int, target: Creature, damage_type: str | DamageType = DamageType.MAGICAL, card=None, source=None, direct: bool | None = None):
        self.damage = damage
        self.target = target
        self.damage_type = _normalize_damage_type(damage_type, direct=bool(direct))
        self.card = card
        self.source = source

    def execute(self) -> None:
        from enemies.base import Enemy
        from engine.game_state import game_state
        from engine.messages import (
            AnyHpLostMessage,
            CreatureDiedMessage,
            DamageDealtMessage,
            FatalDamageMessage,
            PhysicalAttackDealtMessage,
            PhysicalAttackTakenMessage,
        )
        from utils.dynamic_values import resolve_potential_damage

        if not self.target or self.target.is_dead():
            return

        if self.source is not None:
            damage_amount = resolve_potential_damage(
                self.damage,
                self.source,
                self.target,
                card=self.card,
                damage_type=self.damage_type,
            )
        else:
            damage_amount = self.damage
            if callable(damage_amount):
                damage_amount = damage_amount()
            if isinstance(damage_amount, list):
                damage_amount = damage_amount[0] if damage_amount else 0

        block_absorbed = min(self.target.block, damage_amount)
        hp_loss = damage_amount - block_absorbed

        if hp_loss > 0 and hasattr(self.target, "try_prevent_damage") and self.target.try_prevent_damage(hp_loss):
            self.target.block -= block_absorbed
            target_name = getattr(self.target, "name", getattr(self.target, "character", "Unknown"))
            target_name = _localize_character_name(target_name)
            print(t("combat.buffer_prevented", default="{target_name}'s Buffer prevented the damage!", target_name=target_name))
            return

        damage_dealt = self.target.take_damage(
            damage_amount,
            source=self.source,
            card=self.card,
            damage_type=self.damage_type,
        )

        target_name = getattr(self.target, "name", None)
        if target_name is None:
            target_name = getattr(self.target, "character", "Unknown")
        target_name = _localize_character_name(target_name)
        if isinstance(target_name, LocalStr):
            target_name = target_name.resolve()
        print(t("combat.deal_damage_enemy", default="Deal {amount} damage to {target_name}!", amount=damage_dealt, target_name=target_name))

        publish_message(
            DamageDealtMessage(
                amount=damage_dealt,
                target=self.target,
                source=self.source,
                card=self.card,
                damage_type=self.damage_type,
            )
        )
        if damage_dealt > 0:
            publish_message(
                AnyHpLostMessage(
                    target=self.target,
                    amount=damage_dealt,
                    source=self.source,
                    card=self.card,
                )
            )
            if self.damage_type == DamageType.PHYSICAL:
                publish_message(
                    PhysicalAttackTakenMessage(
                        amount=damage_dealt,
                        target=self.target,
                        source=self.source,
                        card=self.card,
                        damage_type=self.damage_type,
                    )
                )
                publish_message(
                    PhysicalAttackDealtMessage(
                        amount=damage_dealt,
                        target=self.target,
                        source=self.source,
                        card=self.card,
                        damage_type=self.damage_type,
                    )
                )

        if isinstance(self.target, Enemy) and self.target.is_dead():
            print(t("combat.enemy_killed", default="Enemy {target_name} has been defeated!", target_name=target_name))
        if self.target.is_dead():
            publish_message(
                FatalDamageMessage(
                    amount=damage_dealt,
                    target=self.target,
                    source=self.source,
                    card=self.card,
                    damage_type=self.damage_type,
                )
            )
            publish_message(
                CreatureDiedMessage(
                    creature=self.target,
                    source=self.source,
                    card=self.card,
                    damage_type=self.damage_type,
                )
            )


@register("action")
class GainBlockAction(Action):
    """Gain block for a creature."""

    def __init__(
        self,
        block: int | Callable[[], int] | None = None,
        target: Creature | None = None,
        source=None,
        card=None,
        amount: int | Callable[[], int] | None = None,
    ):
        if block is None:
            block = amount
        if block is None:
            raise ValueError("GainBlockAction requires 'block' or legacy 'amount'")
        self.block = block
        self.target = target
        self.source = source
        self.card = card

    def execute(self) -> None:
        from engine.messages import BlockGainedMessage

        block_amount = self.block() if callable(self.block) else self.block
        block_amount = int(block_amount)
        if self.target is None:
            return

        self.target.gain_block(block_amount, source=self.source, card=self.card)

        target_name = getattr(self.target, "name", getattr(self.target, "character", "Creature"))
        target_name = _localize_character_name(target_name)
        print(t("combat.gain_block").format(source=target_name, amount=block_amount))
        publish_message(
            BlockGainedMessage(
                target=self.target,
                amount=block_amount,
                source=self.source,
                card=self.card,
            )
        )
