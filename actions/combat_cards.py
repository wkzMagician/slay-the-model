from engine.runtime_api import add_action, add_actions, publish_message, request_input, set_terminal_state
from typing import TYPE_CHECKING, List, Optional

from actions.base import Action
from actions.combat_damage import DealDamageAction, LoseHPAction
from entities.creature import Creature
from localization import LocalStr
from utils.registry import register
from utils.types import TargetType

if TYPE_CHECKING:
    from cards.base import Card


@register("action")
class AttackAction(Action):
    """Publish attack hooks before dealing damage."""

    def __init__(self, damage: int, target: Creature, source: Creature, damage_type: str = "direct", card=None):
        self.damage = damage
        self.target = target
        self.damage_type = damage_type
        self.card = card
        self.source = source

    def execute(self) -> None:
        from engine.game_state import game_state
        from engine.messages import AttackPerformedMessage

        publish_message(
            AttackPerformedMessage(
                target=self.target,
                source=self.source,
                card=self.card,
                damage_type=self.damage_type,
            )
        )

        damage_action = DealDamageAction(
            self.damage,
            target=self.target,
            damage_type=self.damage_type,
            card=self.card,
            source=self.source,
        )
        add_action(damage_action, to_front=True)


@register("action")
class PlayCardAction(Action):
    """Resolve targets and prepare a card play."""

    def __init__(self, card: "Card", is_auto: bool = False, ignore_energy: bool = False):
        self.card = card
        self.is_auto = is_auto
        self.ignore_energy = ignore_energy

    def execute(self) -> None:
        from actions.display import InputRequestAction
        from engine.game_state import game_state
        from localization import LocalStr
        from utils.combat import resolve_target
        from utils.option import Option

        if not self.card:
            return

        can_play, reason = self.card.can_play(self.ignore_energy)
        if not can_play:
            print(f"Cannot play card: {reason}")
            return

        if self.card.target_type == TargetType.ENEMY_SELECT and self.is_auto:
            targets = resolve_target(TargetType.ENEMY_RANDOM)
            add_action(
                PlayCardBHAction(card=self.card, targets=targets, ignore_energy=self.ignore_energy),
                to_front=True,
            )
            return

        assert self.card.target_type is not None
        targets = [target for target in resolve_target(self.card.target_type) if target is not None]
        if self.card.target_type == TargetType.ENEMY_SELECT and len(targets) > 1:
            options = []
            for enemy in targets:
                enemy_name = getattr(enemy, "name", getattr(enemy, "character", "Unknown"))
                if isinstance(enemy_name, LocalStr):
                    enemy_name = enemy_name.resolve()
                options.append(
                    Option(
                        name=LocalStr(
                            "combat.select_enemy_option",
                            default=f"{enemy_name} (HP: {enemy.hp}/{enemy.max_hp})",
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
            add_action(
                InputRequestAction(
                    title=LocalStr("combat.select_target", default="Select Target"),
                    options=options,
                ),
                to_front=True,
            )
            return
        add_action(
            PlayCardBHAction(card=self.card, targets=targets, ignore_energy=self.ignore_energy),
            to_front=True,
        )


@register("action")
class PlayCardBHAction(Action):
    """Finish playing a card once targets are resolved."""

    def __init__(self, card: "Card", targets: List[Optional[Creature]], ignore_energy: bool = False):
        self.card = card
        self.targets = targets
        self.ignore_energy = ignore_energy

    def execute(self) -> None:
        from actions.card import DiscardCardAction, ExhaustCardAction
        from cards.base import COST_X
        from engine.game_state import game_state
        from engine.messages import CardPlayedMessage
        from localization import t
        from utils.types import CardType

        player = game_state.player
        current_combat = game_state.current_combat
        if player is None or current_combat is None:
            return
        enemies = current_combat.enemies
        resolved_targets = [target for target in self.targets if target is not None]
        message_targets: List[Optional[Creature]] = list(resolved_targets)
        current_combat.combat_state.last_card_targets = list(resolved_targets)

        cost = self.card.cost
        if getattr(self.card, "_cost", None) == COST_X:
            cost = player.energy
            setattr(self.card, "_x_cost_energy", cost)
        if cost > 0 and not self.ignore_energy:
            player.gain_energy(-cost)
            current_combat.combat_state.player_energy_spent_this_turn += cost
        self.card.cost_until_played = None

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

        publish_message(
            CardPlayedMessage(
                card=self.card,
                owner=player,
                targets=message_targets,
            )
        )

        current_combat.combat_state.turn_cards_played += 1
        if self.card.card_type == CardType.ATTACK:
            current_combat.combat_state.turn_attack_cards_played += 1
        current_combat.combat_state.player_actions_this_turn += 1

        card_name = self.card.display_name.resolve() if hasattr(self.card, "display_name") else str(self.card)
        print(t("combat.play_card", card=card_name))

        has_medical_kit = any(getattr(relic, "idstr", None) == "MedicalKit" for relic in player.relics)
        should_exhaust_status = has_medical_kit and self.card.card_type == CardType.STATUS
        has_blue_candle = any(getattr(relic, "idstr", None) == "BlueCandle" for relic in player.relics)
        should_exhaust_curse = has_blue_candle and self.card.card_type == CardType.CURSE
        will_exhaust = self.card.get_value("exhaust") is True or should_exhaust_status or should_exhaust_curse

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
            add_action(DiscardCardAction(card=self.card, trigger_effects=False))
        elif will_exhaust:
            add_action(ExhaustCardAction(card=self.card))
        else:
            if is_power_card:
                player.card_manager.remove_from_pile(self.card, "hand")
            else:
                add_action(DiscardCardAction(card=self.card, trigger_effects=False))

        if should_exhaust_curse:
            hp_loss = 1
            for relic in player.relics:
                if getattr(relic, "idstr", None) == "BlueCandle":
                    hook = getattr(relic, "curse_play_hp_loss", None)
                    if hook:
                        hp_loss = hook()
                    break
            add_action(LoseHPAction(amount=hp_loss, target=player, source=self.card))
