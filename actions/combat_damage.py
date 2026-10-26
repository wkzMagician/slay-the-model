from engine.runtime_api import add_action, add_actions, publish_message, request_input, set_terminal_state
from collections.abc import Callable
from typing import TYPE_CHECKING, Any, cast

from actions.base import Action
from entities.creature import Creature
from localization import LocalStr, t
from utils.registry import register
from utils.types import DamageType, TargetType
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


def _resolve_enemy_hp_depletion(
    target: Creature,
    previous_hp: int,
    amount: int,
    source=None,
    card=None,
    damage_type: str | DamageType = DamageType.MAGICAL,
) -> None:
    """Resolve one enemy collapse before deciding permanent death notifications."""
    from enemies.base import Enemy
    from engine.game_state import game_state
    from engine.messages import EnemyHpDepletedMessage, EnemyDefeatedMessage, CreatureDiedMessage, FatalDamageMessage

    if not isinstance(target, Enemy) or previous_hp <= 0 or target.hp > 0:
        return
    # The untyped registry decorator prevents static isinstance narrowing.
    # The runtime guard above establishes the enemy lifecycle contract.
    enemy_target = cast(Enemy, target)
    if getattr(enemy_target, "_hp_depletion_handled", False):
        return

    # Mark before dispatch: reactions may queue further damage or chain kills.
    enemy_target._hp_depletion_handled = True
    enemy_target.on_hp_depleted()
    publish_message(EnemyHpDepletedMessage(
        creature=enemy_target, source=source, card=card, damage_type=damage_type,
        half_dead=enemy_target.half_dead,
    ))
    publish_message(EnemyDefeatedMessage(
        target=enemy_target, source=source, card=card,
        half_dead=enemy_target.half_dead,
    ))
    enemy_target.after_hp_depleted()

    if enemy_target.is_dead() and not getattr(enemy_target, "_death_notified", False):
        enemy_target._death_notified = True
        publish_message(FatalDamageMessage(
            target=enemy_target, amount=amount, source=source, card=card,
            damage_type=damage_type,
        ))
        publish_message(CreatureDiedMessage(
            creature=enemy_target, source=source, card=card, damage_type=damage_type,
        ))

    # The last linked enemy collapsing can make earlier half-dead enemies
    # permanently dead. They already ran their power reactions on collapse,
    # and must not receive another killing-blow reward for this damage.
    combat = game_state.current_combat
    for enemy in list(combat.enemies) if combat is not None else []:
        if (enemy is not enemy_target and getattr(enemy, "_hp_depletion_handled", False)
                and enemy.is_dead() and not getattr(enemy, "_death_notified", False)):
            enemy._death_notified = True
            publish_message(CreatureDiedMessage(
                creature=enemy, source=source, card=None, damage_type=damage_type,
            ))


def _publish_death_notifications(
    target: Creature,
    amount: int,
    source=None,
    card=None,
    damage_type: str | DamageType = DamageType.MAGICAL,
) -> None:
    from engine.messages import CreatureDiedMessage, FatalDamageMessage

    publish_message(FatalDamageMessage(
        target=target, amount=amount, source=source, card=card,
        damage_type=damage_type,
    ))
    publish_message(CreatureDiedMessage(
        creature=target, source=source, card=card, damage_type=damage_type,
    ))


def _resolve_player_hp_depletion(
    target: Creature,
    previous_hp: int,
    amount: int,
    source=None,
    card=None,
    damage_type: str | DamageType = DamageType.MAGICAL,
) -> None:
    """Complete revival synchronously, or notify actual player death once."""
    from player.player import Player

    if not isinstance(target, Player) or previous_hp <= 0 or target.hp > 0:
        return
    if target.try_revive():
        return
    _publish_death_notifications(target, amount, source, card, damage_type)


@register("action")
class HealAction(Action):
    """Heal a creature for a specified amount or percentage."""

    preserve_after_combat = True

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

    preserve_after_combat = True

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

        # A defeated player cannot consume another revival item or die twice.
        # Enemy zero-HP reactions retain their separate half-dead protocol.
        from player.player import Player
        if isinstance(lose_target, Player) and lose_target.is_dead():
            return

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
            _resolve_enemy_hp_depletion(
                lose_target, old_hp, lost, source=self.source, card=self.card,
                damage_type=DamageType.HP_LOSS,
            )
            _resolve_player_hp_depletion(
                lose_target, old_hp, lost, source=self.source, card=self.card,
                damage_type=DamageType.HP_LOSS,
            )
            from actions.combat_cleanup import clear_post_combat_actions_if_finished
            clear_post_combat_actions_if_finished()


@register("action")
class DealDamageAction(Action):
    """Deal damage to a target creature."""

    preserve_after_combat = True

    def __init__(self, damage: int, target: Creature, damage_type: str | DamageType = DamageType.MAGICAL, card=None, source=None, direct: bool | None = None, *, cancel_on_source_death: bool | None = None, damage_is_calculated: bool = False):
        self.damage = damage
        self.target = target
        self.damage_type = _normalize_damage_type(damage_type, direct=bool(direct))
        self.card = card
        self.source = source
        self.damage_is_calculated = damage_is_calculated
        # Ordinary single-target attacks follow DamageAction's source guard.
        # AoE producers opt out; magical/orb/power effects have other contracts.
        self.cancel_on_source_death = (
            self.damage_type == DamageType.PHYSICAL and getattr(card, "target_type", None) != TargetType.ENEMY_ALL
            if cancel_on_source_death is None else cancel_on_source_death
        )

    def should_cancel_source(self) -> bool:
        """Check the current source, including temporary zero-HP phases."""
        # Pickled queues from before this policy field was added retain their
        # known card AoE contract instead of failing or gaining a new guard.
        cancel_on_source_death = getattr(
            self, "cancel_on_source_death",
            self.damage_type == DamageType.PHYSICAL and getattr(self.card, "target_type", None) != TargetType.ENEMY_ALL,
        )
        return (
            cancel_on_source_death
            and self.damage_type != DamageType.THORNS
            and isinstance(self.source, Creature)
            and (self.source.is_dead() or bool(getattr(self.source, "half_dead", False)))
        )

    def execute(self) -> None:
        from enemies.base import Enemy
        from player.player import Player
        from engine.game_state import game_state
        from engine.messages import (
            AnyHpLostMessage,
            CreatureDiedMessage,
            DamageDealtMessage,
            FatalDamageMessage,
            PhysicalAttackDealtMessage,
            PhysicalAttackTakenMessage,
        )
        from utils.dynamic_values import resolve_calculated_damage, resolve_potential_damage

        if not self.target or self.target.is_dead():
            return
        if self.should_cancel_source():
            return

        if getattr(self, "damage_is_calculated", False):
            damage_amount = resolve_calculated_damage(
                self.damage, self.source, self.target, self.damage_type,
            )
        else:
            damage_amount = resolve_potential_damage(
                self.damage, self.source, self.target,
                card=self.card, damage_type=self.damage_type,
            )

        block_absorbed = min(self.target.block, damage_amount)
        hp_loss = damage_amount - block_absorbed

        if hp_loss > 0 and hasattr(self.target, "try_prevent_damage") and self.target.try_prevent_damage(hp_loss):
            self.target.block -= block_absorbed
            target_name = getattr(self.target, "name", getattr(self.target, "character", "Unknown"))
            target_name = _localize_character_name(target_name)
            print(t("combat.buffer_prevented", default="{target_name}'s Buffer prevented the damage!", target_name=target_name))
            return

        old_hp = self.target.hp
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
        if isinstance(self.target, Enemy):
            _resolve_enemy_hp_depletion(
                self.target, old_hp, damage_dealt, source=self.source,
                card=self.card, damage_type=self.damage_type,
            )
        elif isinstance(self.target, Player):
            _resolve_player_hp_depletion(
                self.target, old_hp, damage_dealt, source=self.source,
                card=self.card, damage_type=self.damage_type,
            )
        elif self.target.is_dead():
            _publish_death_notifications(
                self.target, damage_dealt, source=self.source,
                card=self.card, damage_type=self.damage_type,
            )
        from actions.combat_cleanup import clear_post_combat_actions_if_finished
        clear_post_combat_actions_if_finished()


@register("action")
class GainBlockAction(Action):
    """Gain block for a creature."""

    preserve_after_combat = True

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
