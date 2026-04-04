"""Watcher shared card helpers."""

from __future__ import annotations

import random
from typing import Any, List

from actions.card import AddCardAction, DrawCardsAction
from actions.card_choice import ChooseAddRandomCardAction, ChooseCardLambdaAction, MoveCardAction, SetCostUntilEndOfTurnAction
from actions.card_lifecycle import ExhaustCardAction
from actions.combat import EndTurnAction, GainBlockAction, GainEnergyAction
from actions.combat_cards import AttackAction, PlayCardAction
from actions.combat_damage import LoseHPAction
from actions.combat_status import ApplyPowerAction
from actions.display import InputRequestAction
from actions.watcher import ChangeStanceAction, GainMantraAction, ReturnCardToHandAction, ScryAction, SkipEnemyTurnAction, TriggerMarkAction
from cards.base import COST_UNPLAYABLE, COST_X, Card, RawLocalStr
from engine.messages import ScryMessage, StanceChangedMessage
from engine.runtime_api import add_action, add_actions
from engine.subscriptions import MessagePriority, subscribe
from powers.definitions.dexterity import DexterityPower
from powers.definitions.draw_card_next_turn import DrawCardNextTurnPower
from powers.definitions.plated_armor import PlatedArmorPower
from powers.definitions.strength import StrengthPower
from powers.definitions.vulnerable import VulnerablePower
from powers.definitions.weak import WeakPower
from powers.definitions.watcher import (
    BattleHymnPower,
    BlasphemerPower,
    CollectPower,
    DevotionPower,
    EstablishmentPower,
    FastingPower,
    ForesightPower,
    LikeWaterPower,
    MarkPower,
    MasterRealityPower,
    MentalFortressPower,
    NirvanaPower,
    OmegaPower,
    RushdownPower,
    TalkToTheHandPower,
    WaveOfTheHandPower,
    WreathOfFlamePower,
)
from utils.dynamic_values import resolve_potential_damage
from utils.option import Option
from utils.registry import register
from utils.types import CardType, RarityType, StatusType, TargetType


class _SafeFormatDict(dict[str, Any]):
    def __missing__(self, key: str) -> str:
        return "{" + key + "}"


class StaticTextMixin:
    def _text_for_field(self, field: str) -> str:
        mapping = {
            "name": getattr(self, "text_name", ""),
            "description": getattr(self, "text_description", ""),
            "upgrade_description": getattr(self, "text_upgrade_description", ""),
            "combat_description": getattr(self, "text_combat_description", "") or getattr(self, "text_description", ""),
            "upgrade_combat_description": getattr(self, "text_upgrade_combat_description", "") or getattr(self, "text_upgrade_description", ""),
        }
        return mapping.get(field, "")

    def local(self, field: str, **kwargs: Any) -> RawLocalStr:
        template = self._text_for_field(field)
        if not template:
            return RawLocalStr("")
        try:
            return RawLocalStr(template.format_map(_SafeFormatDict(kwargs)))
        except Exception:
            return RawLocalStr(template)

    def has_local(self, field: str) -> bool:
        return bool(self._text_for_field(field))


def _player():
    from engine.game_state import game_state

    return game_state.player


def _combat():
    from engine.game_state import game_state

    return game_state.current_combat


def _alive_enemies():
    combat = _combat()
    return [enemy for enemy in (combat.enemies if combat else []) if not enemy.is_dead()]


def _last_played_card():
    player = _player()
    if player is None:
        return None
    discard = player.card_manager.get_pile("discard_pile")
    return discard[-1] if discard else None


class WatcherCard(StaticTextMixin, Card):
    text_name = ""
    text_description = ""


class WatcherAttack(WatcherCard):
    card_type = CardType.ATTACK
    target_type = TargetType.ENEMY_SELECT


class WatcherSkill(WatcherCard):
    card_type = CardType.SKILL
    target_type = TargetType.SELF


class WatcherPowerCard(WatcherCard):
    card_type = CardType.POWER
    target_type = TargetType.SELF


__all__ = [
    "AddCardAction",
    "Any",
    "ApplyPowerAction",
    "AttackAction",
    "BattleHymnPower",
    "BlasphemerPower",
    "COST_UNPLAYABLE",
    "COST_X",
    "Card",
    "CardType",
    "ChangeStanceAction",
    "ChooseAddRandomCardAction",
    "ChooseCardLambdaAction",
    "CollectPower",
    "DevotionPower",
    "DexterityPower",
    "DrawCardNextTurnPower",
    "DrawCardsAction",
    "EndTurnAction",
    "EstablishmentPower",
    "ExhaustCardAction",
    "FastingPower",
    "ForesightPower",
    "GainBlockAction",
    "GainEnergyAction",
    "GainMantraAction",
    "InputRequestAction",
    "LikeWaterPower",
    "List",
    "LoseHPAction",
    "MarkPower",
    "MasterRealityPower",
    "MentalFortressPower",
    "MessagePriority",
    "MoveCardAction",
    "NirvanaPower",
    "OmegaPower",
    "Option",
    "PlayCardAction",
    "PlatedArmorPower",
    "RarityType",
    "RawLocalStr",
    "ReturnCardToHandAction",
    "RushdownPower",
    "ScryAction",
    "ScryMessage",
    "SetCostUntilEndOfTurnAction",
    "SkipEnemyTurnAction",
    "StaticTextMixin",
    "StatusType",
    "StanceChangedMessage",
    "StrengthPower",
    "TalkToTheHandPower",
    "TargetType",
    "TriggerMarkAction",
    "VulnerablePower",
    "WatcherAttack",
    "WatcherCard",
    "WatcherPowerCard",
    "WatcherSkill",
    "WaveOfTheHandPower",
    "WeakPower",
    "WreathOfFlamePower",
    "_alive_enemies",
    "_combat",
    "_last_played_card",
    "_player",
    "add_action",
    "add_actions",
    "random",
    "register",
    "resolve_potential_damage",
    "subscribe",
]
