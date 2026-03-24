from typing import TYPE_CHECKING, Any

from actions.base import Action
from entities.creature import Creature
from localization import LocalStr, t
from utils.registry import register
from utils.result_types import BaseResult, MultipleActionsResult, NoneResult

if TYPE_CHECKING:
    from enemies.base import Enemy


def _localize_character_name(raw_name: str) -> str:
    """Convert English character name to localized version."""
    if raw_name in ("Ironclad", "Silent", "Defect", "Watcher"):
        return t(f"ui.character.{raw_name.lower()}", default=raw_name)
    return raw_name


@register("action")
class HealAction(Action):
    """Heal a creature for a specified amount or percentage."""

    def __init__(self, amount: int | None = None, percent: float | None = None, target: Creature = None):
        self.amount = amount
        self.percent = percent
        self.target = target

    def execute(self) -> BaseResult:
        from engine.game_state import game_state
        from engine.messages import HealedMessage

        actions_to_return = []
        heal_target = self.target if self.target else game_state.player

        if heal_target:
            if self.percent is not None:
                heal_amount = int(heal_target.max_hp * self.percent)
            else:
                heal_amount = self.amount() if callable(self.amount) else (self.amount or 0)

            if heal_target == game_state.player:
                for relic in list(game_state.player.relics):
                    if hasattr(relic, "modify_heal"):
                        heal_amount = relic.modify_heal(heal_amount)
            if hasattr(heal_target, "powers"):
                for power in list(heal_target.powers):
                    if hasattr(power, "modify_heal"):
                        heal_amount = power.modify_heal(heal_amount)
            heal_amount = max(0, int(heal_amount))

            old_hp = heal_target.hp
            heal_target.hp = min(heal_target.hp + heal_amount, heal_target.max_hp)
            healed = heal_target.hp - old_hp
            print(t("ui.healed", default=f"Healed for {healed} HP.", amount=healed))
            participants = [heal_target]
            if heal_target == game_state.player:
                participants.extend(list(game_state.player.relics))
            actions_to_return.extend(
                game_state.publish_message(
                    HealedMessage(
                        target=heal_target,
                        amount=healed,
                        previous_hp=old_hp,
                        new_hp=heal_target.hp,
                        source=self,
                    ),
                    participants=participants,
                )
            )

        if actions_to_return:
            return MultipleActionsResult(actions_to_return)
        return NoneResult()


@register("action")
class LoseHPAction(Action):
    """Make a creature lose HP without interacting with block."""

    def __init__(self, amount: int | None = None, percent: float | None = None, target: Creature = None, card=None, source=None):
        self.amount = amount
        self.percent = percent
        self.target = target
        self.card = card
        self.source = source

    def execute(self) -> BaseResult:
        from engine.game_state import game_state
        from engine.messages import HpLostMessage

        actions_to_return = []
        lose_target = self.target if self.target else game_state.player

        if lose_target:
            if self.percent is not None:
                hp_loss = int(lose_target.max_hp * self.percent)
            else:
                hp_loss = self.amount() if callable(self.amount) else (self.amount or 0)

            if lose_target.try_prevent_damage(hp_loss):
                print(t("ui.hp_loss_prevented", default="HP loss prevented.", amount=hp_loss))
                return NoneResult()

            old_hp = lose_target.hp
            lose_target.hp -= hp_loss
            lost = old_hp - lose_target.hp
            print(t("ui.lost_hp", default=f"Lost {lost} HP.", amount=lost))
            participants = [*list(getattr(lose_target, "powers", [])), lose_target]
            actions_to_return.extend(
                game_state.publish_message(
                    HpLostMessage(
                        target=lose_target,
                        amount=lost,
                        source=self.source,
                        card=self.card,
                    ),
                    participants=participants,
                )
            )

        if actions_to_return:
            return MultipleActionsResult(actions_to_return)
        return NoneResult()


@register("action")
class DealDamageAction(Action):
    """Deal damage to a target creature."""

    def __init__(self, damage: int, target: Creature, damage_type: str = "direct", card=None, source=None):
        self.damage = damage
        self.target = target
        self.damage_type = damage_type
        self.card = card
        self.source = source

    def execute(self) -> BaseResult:
        from enemies.base import Enemy
        from engine.game_state import game_state
        from engine.messages import CreatureDiedMessage, DamageResolvedMessage
        from utils.dynamic_values import resolve_potential_damage

        actions_to_return = []

        if not self.target or self.target.is_dead():
            return NoneResult()

        if self.source is not None:
            damage_amount = resolve_potential_damage(self.damage, self.source, self.target, card=self.card)
        else:
            damage_amount = self.damage
            if callable(damage_amount):
                damage_amount = damage_amount()
            if isinstance(damage_amount, list):
                damage_amount = damage_amount[0] if damage_amount else 0

        if hasattr(self.target, "try_prevent_damage") and self.target.try_prevent_damage(damage_amount):
            target_name = getattr(self.target, "name", getattr(self.target, "character", "Unknown"))
            target_name = _localize_character_name(target_name)
            print(t("combat.buffer_prevented", default="{target_name}'s Buffer prevented the damage!", target_name=target_name))
            return NoneResult()

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

        participants = [*list(getattr(self.target, "powers", [])), self.target]
        if self.source is not None:
            participants.append(self.source)
        if self.card is not None:
            participants.append(self.card)
        player = getattr(game_state, "player", None)
        if player is not None:
            participants.extend(list(player.relics))

        actions_to_return.extend(
            game_state.publish_message(
                DamageResolvedMessage(
                    amount=damage_dealt,
                    target=self.target,
                    source=self.source,
                    card=self.card,
                    damage_type=self.damage_type,
                ),
                participants=participants,
            )
        )

        if isinstance(self.target, Enemy) and self.target.is_dead():
            print(t("combat.enemy_killed", default="Enemy {target_name} has been defeated!", target_name=target_name))
        if self.target.is_dead():
            actions_to_return.extend(
                game_state.publish_message(
                    CreatureDiedMessage(
                        creature=self.target,
                        source=self.source,
                        card=self.card,
                        damage_type=self.damage_type,
                    ),
                    participants=[self.target],
                )
            )

        if actions_to_return:
            return MultipleActionsResult(actions_to_return)
        return NoneResult()


@register("action")
class GainBlockAction(Action):
    """Gain block for a creature."""

    def __init__(self, block=None, target: Creature = None, source=None, card=None, amount=None):
        if block is None:
            block = amount
        if block is None:
            raise ValueError("GainBlockAction requires 'block' or legacy 'amount'")
        self.block = block
        self.target = target
        self.source = source
        self.card = card

    def execute(self) -> BaseResult:
        from engine.game_state import game_state
        from engine.messages import BlockGainedMessage

        actions_to_return = []
        block_amount = self.block() if callable(self.block) else self.block

        self.target.gain_block(block_amount, source=self.source, card=self.card)

        target_name = getattr(self.target, "name", getattr(self.target, "character", "Creature"))
        target_name = _localize_character_name(target_name)
        print(t("combat.gain_block").format(source=target_name, amount=block_amount))
        actions_to_return.extend(
            game_state.publish_message(
                BlockGainedMessage(
                    target=self.target,
                    amount=block_amount,
                    source=self.source,
                    card=self.card,
                ),
                participants=[self.target, *list(getattr(self.target, "powers", []))],
            )
        )

        if actions_to_return:
            return MultipleActionsResult(actions_to_return)
        return NoneResult()
