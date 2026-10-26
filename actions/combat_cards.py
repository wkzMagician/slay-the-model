from engine.runtime_api import add_action, add_actions, publish_message, request_input, set_terminal_state
from typing import TYPE_CHECKING, List, Optional

from actions.base import Action
from actions.combat_damage import DealDamageAction, LoseHPAction
from actions.card_play_lifecycle import CardPlayRequest, queue_card_play, put_in_limbo, finalize_card_play
from entities.creature import Creature
from localization import LocalStr
from utils.registry import register
from utils.types import DamageType, TargetType

if TYPE_CHECKING:
    from cards.base import Card


def _build_enemy_target_option_name(card: "Card", enemy: Creature) -> LocalStr:
    enemy_name = getattr(enemy, "name", getattr(enemy, "character", "Unknown"))
    if isinstance(enemy_name, LocalStr):
        enemy_name = enemy_name.resolve()

    preview_parts = [f"HP: {enemy.hp}/{enemy.max_hp}"]
    if getattr(enemy, "block", 0) > 0:
        preview_parts.append(f"Block: {enemy.block}")
    preview_text = card.get_combat_description(target=enemy).resolve()

    return LocalStr(
        "combat.select_enemy_option",
        default=f"{enemy_name} ({', '.join(preview_parts)})\n  -> {preview_text}",
    )


@register("action")
class AttackAction(Action):
    """Publish attack hooks before dealing damage."""

    preserve_after_combat = True
    damage_action_type = DealDamageAction

    def __init__(self, damage: int, target: Creature, source: Creature, damage_type: str | DamageType = DamageType.PHYSICAL, card=None, *, cancel_on_source_death: bool | None = None):
        self.damage = damage
        self.target = target
        self.damage_type = damage_type
        self.card = card
        self.source = source
        self.cancel_on_source_death = cancel_on_source_death
        self.damage_is_calculated = card is not None and damage_type in (DamageType.PHYSICAL, "attack")
        if self.damage_is_calculated:
            from utils.dynamic_values import resolve_potential_damage
            self.damage = resolve_potential_damage(
                damage, source, target, card=card, damage_type=damage_type,
                for_card_snapshot=True,
            )

    def execute(self) -> None:
        from engine.game_state import game_state
        from engine.messages import AttackPerformedMessage

        damage_action = self.damage_action_type(
            self.damage,
            target=self.target,
            damage_type=self.damage_type,
            card=self.card,
            source=self.source,
            cancel_on_source_death=getattr(self, "cancel_on_source_death", None),
            damage_is_calculated=getattr(self, "damage_is_calculated", False),
        )
        # DamageAction's guard also precedes attack side effects such as theft.
        # Check again inside the damage action if the source changes meanwhile.
        if damage_action.should_cancel_source():
            return

        publish_message(
            AttackPerformedMessage(
                target=self.target,
                source=self.source,
                card=self.card,
                damage_type=self.damage_type,
            )
        )

        add_action(damage_action, to_front=True)


@register("action")
class RandomCardAttackAction(Action):
    """Select a living target and recalculate the card for this hit only."""

    preserve_after_combat = True

    def __init__(self, card: "Card", source: Creature):
        self.card = card
        self.source = source

    def execute(self) -> None:
        import random
        from engine.game_state import game_state
        from utils.dynamic_values import attack_base_damage

        if self.source.is_dead() or getattr(self.source, "half_dead", False):
            return
        combat = game_state.current_combat
        if combat is None:
            return
        enemies = [enemy for enemy in combat.enemies
                   if enemy.is_alive and not enemy.half_dead]
        if not enemies:
            return
        target = random.choice(enemies)
        add_action(AttackAction(
            attack_base_damage(self.card), target=target,
            source=self.source, card=self.card,
        ), to_front=True)


@register("action")
class PlayCardAction(Action):
    """Resolve targets and prepare a card play."""

    def __init__(self, card: "Card", is_auto: bool = False, ignore_energy: bool = False, *, request: CardPlayRequest | None = None):
        self.card = card
        self.is_auto = is_auto
        self.ignore_energy = ignore_energy
        self.request = request

    def execute(self) -> None:
        from actions.display import InputRequestAction
        from engine.game_state import game_state
        from localization import LocalStr
        from utils.combat import resolve_target
        from utils.option import Option

        if not self.card:
            return

        request = getattr(self, "request", None)
        if self.is_auto and request is None:
            queue_card_play(self.card)
            return
        can_play, reason = self.card.can_play(self.ignore_energy)
        if not can_play:
            print(f"Cannot play card: {reason}")
            if request is not None:
                request.cancelled = True
                finalize_card_play(request)
            return

        if (request is not None and request.targets is not None
                and self.card.target_type == TargetType.ENEMY_SELECT):
            targets = [target for target in request.targets
                       if not target.is_dead() and not getattr(target, "half_dead", False)]
            if not targets:
                request.cancelled = True
                finalize_card_play(request)
                return
            add_action(PlayCardBHAction(self.card, targets, self.ignore_energy,
                                       request=request), to_front=True)
            return
        if self.card.target_type == TargetType.ENEMY_SELECT and self.is_auto:
            targets = resolve_target(TargetType.ENEMY_RANDOM)
            if not any(target is not None for target in targets):
                if request is not None:
                    request.cancelled = True
                    finalize_card_play(request)
                return
            add_action(
                PlayCardBHAction(card=self.card, targets=targets, ignore_energy=self.ignore_energy, request=request),
                to_front=True,
            )
            return

        assert self.card.target_type is not None
        # Random card attacks choose per hit; resolving here consumes an extra
        # random choice and incorrectly binds the whole card to one enemy.
        targets = ([] if self.card.target_type == TargetType.ENEMY_RANDOM else
                   [target for target in resolve_target(self.card.target_type) if target is not None])
        if self.card.target_type == TargetType.ENEMY_SELECT and targets:
            options = []
            for enemy in targets:
                options.append(
                    Option(
                        name=_build_enemy_target_option_name(self.card, enemy),
                        actions=[
                            PlayCardBHAction(
                                card=self.card,
                                targets=[enemy],
                                ignore_energy=self.ignore_energy,
                                request=request,
                            )
                        ],
                    )
                )
            options.append(
                Option(
                    name=LocalStr("ui.cancel_target_selection", default="Cancel"),
                    actions=[],
                    commands=["cancel", "back"],
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
        add_action(
            PlayCardBHAction(card=self.card, targets=targets, ignore_energy=self.ignore_energy, request=request),
            to_front=True,
        )


@register("action")
class PlayCardBHAction(Action):
    """Finish playing a card once targets are resolved."""

    def __init__(self, card: "Card", targets: List[Optional[Creature]], ignore_energy: bool = False, *, request: CardPlayRequest | None = None):
        self.card = card
        self.targets = targets
        self.ignore_energy = ignore_energy
        self.request = request

    def execute(self) -> None:
        from cards.base import COST_X
        from engine.game_state import game_state
        from engine.messages import CardPlayedMessage
        from localization import t
        from utils.types import CardType

        player = game_state.player
        current_combat = game_state.current_combat
        if player is None or current_combat is None:
            return
        request = getattr(self, "request", None)
        if request is None:
            request = CardPlayRequest(self.card, is_auto=False,
                                      ignore_energy=self.ignore_energy)
        if request.started or request.finalized:
            return
        request.started = True
        put_in_limbo(self.card)
        if not hasattr(game_state, "active_card_plays"):
            game_state.active_card_plays = []
        game_state.active_card_plays.append(request)
        enemies = current_combat.enemies
        resolved_targets = [target for target in self.targets if target is not None]
        message_targets: List[Optional[Creature]] = list(resolved_targets)
        if self.card.target_type == TargetType.ENEMY_RANDOM:
            # Enemy card-play observers still see the play even though its
            # actual attack targets will only be selected by the hit actions.
            message_targets = [enemy for enemy in enemies if enemy.is_alive and not enemy.half_dead]
        current_combat.combat_state.last_card_targets = list(resolved_targets)

        cost = self.card.cost
        if getattr(self.card, "_cost", None) == COST_X:
            cost = request.energy_on_use if request.energy_on_use is not None else player.energy
            setattr(self.card, "_x_cost_energy", cost)
        if cost > 0 and not self.ignore_energy:
            player.gain_energy(-cost)
            current_combat.combat_state.player_energy_spent_this_turn += cost

        if len(resolved_targets) == 1:
            target = resolved_targets[0]
            from enemies.base import Enemy
            if isinstance(target, Enemy):
                from engine.back_attack_manager import BackAttackManager
                manager = BackAttackManager()
                manager.maybe_transfer_on_target(target)

        play_actions = self.card.on_play(targets=resolved_targets)
        if play_actions:
            add_actions(play_actions)
        current_combat.combat_state.last_played_card = self.card

        current_combat.combat_state.turn_cards_played += 1
        if self.card.card_type == CardType.ATTACK:
            current_combat.combat_state.turn_attack_cards_played += 1
        if self.card.card_type == CardType.POWER:
            current_combat.combat_state.power_cards_played += 1
        current_combat.combat_state.player_actions_this_turn += 1

        publish_message(
            CardPlayedMessage(
                card=self.card,
                owner=player,
                targets=message_targets,
            )
        )

        card_name = self.card.display_name.resolve() if hasattr(self.card, "display_name") else str(self.card)
        print(t("combat.play_card", card=card_name))

        has_medical_kit = any(getattr(relic, "idstr", None) == "MedicalKit" for relic in player.relics)
        should_exhaust_status = has_medical_kit and self.card.card_type == CardType.STATUS
        has_blue_candle = any(getattr(relic, "idstr", None) == "BlueCandle" for relic in player.relics)
        should_exhaust_curse = has_blue_candle and self.card.card_type == CardType.CURSE
        has_corruption = (
            self.card.card_type == CardType.SKILL
            and player.get_power("Corruption") is not None
        )
        will_exhaust = (
            self.card.get_value("exhaust") is True
            or should_exhaust_status
            or should_exhaust_curse
            or has_corruption
        )

        request.will_exhaust = will_exhaust

        if should_exhaust_curse:
            hp_loss = 1
            for relic in player.relics:
                if getattr(relic, "idstr", None) == "BlueCandle":
                    hook = getattr(relic, "curse_play_hp_loss", None)
                    if hook:
                        hp_loss = hook()
                    break
            add_action(LoseHPAction(amount=hp_loss, target=player, source=self.card))


