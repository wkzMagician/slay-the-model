"""Explicit message subscriber contracts."""
from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import Callable, Iterable, Tuple

from engine.messages import (
    EXPLICIT_SUBSCRIPTION_MESSAGE_TYPES,
    AttackPerformedMessage,
    BlockGainedMessage,
    CardAddedToPileMessage,
    CardDiscardedMessage,
    CardDrawnMessage,
    CardExhaustedMessage,
    CardPlayedMessage,
    CombatEndedMessage,
    CombatStartedMessage,
    CreatureDiedMessage,
    DamageDealtMessage,
    DirectHpLossMessage,
    EliteVictoryMessage,
    FatalDamageMessage,
    GameMessage,
    GoldGainedMessage,
    HealedMessage,
    HpLostMessage,
    AnyHpLostMessage,
    PhysicalAttackDealtMessage,
    PhysicalAttackTakenMessage,
    PlayerTurnPostDrawMessage,
    PlayerTurnEndedMessage,
    PlayerTurnStartedMessage,
    PotionUsedMessage,
    PowerAppliedMessage,
    RelicObtainedMessage,
    ScryMessage,
    ShuffleMessage,
    ShopEnteredMessage,
    StanceChangedMessage,
)

ParameterNames = Tuple[str, ...]
Predicate = Callable[[Callable, GameMessage], bool]
Binder = Callable[[Callable, GameMessage], object]


def subscription_parameter_names(func: Callable, *, bound: bool) -> ParameterNames:
    """Return declared subscriber parameter names, excluding ``self`` when needed."""
    signature = inspect.signature(func)
    names = []
    for parameter in signature.parameters.values():
        if parameter.kind not in (
            inspect.Parameter.POSITIONAL_ONLY,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
        ):
            raise TypeError("Subscriber signatures may only use positional parameters")
        names.append(parameter.name)
    if not bound and names and names[0] in {"self", "cls"}:
        names = names[1:]
    return tuple(names)


_ALWAYS: Predicate = lambda _bound_method, _message: True


@dataclass(frozen=True)
class MessageContract:
    message_type: type[GameMessage]
    param_names: ParameterNames
    binder: Binder
    predicate: Predicate = _ALWAYS

    def supports(self, param_names: Iterable[str], method_name: str | None = None) -> bool:
        names = tuple(param_names)
        return self.param_names == names


def _bind(*value_getters: Callable[[Callable, GameMessage], object]) -> Binder:
    def binder(bound_method: Callable, message: GameMessage):
        return bound_method(*(getter(bound_method, message) for getter in value_getters))

    return binder


def _bind_with_previous_hp(*value_getters: Callable[[Callable, GameMessage], object]) -> Binder:
    def binder(bound_method: Callable, message: GameMessage):
        target = getattr(message, "target", None)
        current_hp = getattr(target, "hp", None)
        previous_hp = getattr(message, "previous_hp", None)

        def call():
            return bound_method(*(getter(bound_method, message) for getter in value_getters))

        if target is None or previous_hp is None or current_hp is None:
            return call()
        target.hp = previous_hp
        try:
            return call()
        finally:
            target.hp = current_hp

    return binder


_TARGETS = lambda _bound_method, message: message.targets
_FLOOR = lambda _bound_method, message: message.floor
_AMOUNT = lambda _bound_method, message: message.amount
_COUNT = lambda _bound_method, message: message.count
_CARD = lambda _bound_method, message: message.card
_DEST_PILE = lambda _bound_method, message: message.dest_pile
_SOURCE_PILE = lambda _bound_method, message: message.source_pile
_POTION = lambda _bound_method, message: message.potion
_TARGET = lambda _bound_method, message: message.target
_SOURCE = lambda _bound_method, message: message.source
_POWER = lambda _bound_method, message: message.power
_DAMAGE_TYPE = lambda _bound_method, message: message.damage_type
_PREVIOUS_STATUS = lambda _bound_method, message: message.previous_status
_NEW_STATUS = lambda _bound_method, message: message.new_status


def _build_contracts() -> dict[type[GameMessage], MessageContract]:
    contracts = {
        CombatStartedMessage: MessageContract(
            message_type=CombatStartedMessage,
            param_names=("floor",),
            binder=_bind(_FLOOR),
        ),
        CombatEndedMessage: MessageContract(
            message_type=CombatEndedMessage,
            param_names=(),
            binder=_bind(),
        ),
        PlayerTurnStartedMessage: MessageContract(
            message_type=PlayerTurnStartedMessage,
            param_names=(),
            binder=_bind(),
        ),
        PlayerTurnEndedMessage: MessageContract(
            message_type=PlayerTurnEndedMessage,
            param_names=(),
            binder=_bind(),
        ),
        PlayerTurnPostDrawMessage: MessageContract(
            message_type=PlayerTurnPostDrawMessage,
            param_names=(),
            binder=_bind(),
        ),
        StanceChangedMessage: MessageContract(
            message_type=StanceChangedMessage,
            param_names=("previous_status", "new_status"),
            binder=_bind(_PREVIOUS_STATUS, _NEW_STATUS),
        ),
        ScryMessage: MessageContract(
            message_type=ScryMessage,
            param_names=("count",),
            binder=_bind(_COUNT),
        ),
        RelicObtainedMessage: MessageContract(
            message_type=RelicObtainedMessage,
            param_names=(),
            binder=_bind(),
        ),
        GoldGainedMessage: MessageContract(
            message_type=GoldGainedMessage,
            param_names=("gold_amount",),
            binder=_bind(_AMOUNT),
        ),
        ShuffleMessage: MessageContract(
            message_type=ShuffleMessage,
            param_names=(),
            binder=_bind(),
        ),
        PotionUsedMessage: MessageContract(
            message_type=PotionUsedMessage,
            param_names=("potion",),
            binder=_bind(_POTION),
        ),
        CardDrawnMessage: MessageContract(
            message_type=CardDrawnMessage,
            param_names=("card",),
            binder=_bind(_CARD),
        ),
        CardDiscardedMessage: MessageContract(
            message_type=CardDiscardedMessage,
            param_names=("card",),
            binder=_bind(_CARD),
        ),
        CardAddedToPileMessage: MessageContract(
            message_type=CardAddedToPileMessage,
            param_names=("card", "dest_pile"),
            binder=_bind(_CARD, _DEST_PILE),
        ),
        CardExhaustedMessage: MessageContract(
            message_type=CardExhaustedMessage,
            param_names=("card", "source_pile"),
            binder=_bind(_CARD, _SOURCE_PILE),
        ),
        CardPlayedMessage: MessageContract(
            message_type=CardPlayedMessage,
            param_names=("card", "targets"),
            binder=_bind(_CARD, _TARGETS),
        ),
        AttackPerformedMessage: MessageContract(
            message_type=AttackPerformedMessage,
            param_names=("target", "source", "card"),
            binder=_bind(_TARGET, _SOURCE, _CARD),
        ),
        PowerAppliedMessage: MessageContract(
            message_type=PowerAppliedMessage,
            param_names=("power", "target"),
            binder=_bind(_POWER, _TARGET),
        ),
        HealedMessage: MessageContract(
            message_type=HealedMessage,
            param_names=("amount", "source"),
            binder=_bind_with_previous_hp(_AMOUNT, _SOURCE),
        ),
        HpLostMessage: MessageContract(
            message_type=HpLostMessage,
            param_names=(),
            binder=_bind(),
        ),
        DirectHpLossMessage: MessageContract(
            message_type=DirectHpLossMessage,
            param_names=("amount", "source", "card"),
            binder=_bind(_AMOUNT, _SOURCE, _CARD),
        ),
        AnyHpLostMessage: MessageContract(
            message_type=AnyHpLostMessage,
            param_names=("amount", "source", "card"),
            binder=_bind(_AMOUNT, _SOURCE, _CARD),
        ),
        BlockGainedMessage: MessageContract(
            message_type=BlockGainedMessage,
            param_names=("amount", "source", "card"),
            binder=_bind(_AMOUNT, _SOURCE, _CARD),
        ),
        DamageDealtMessage: MessageContract(
            message_type=DamageDealtMessage,
            param_names=("damage", "target", "source", "card", "damage_type"),
            binder=_bind(_AMOUNT, _TARGET, _SOURCE, _CARD, _DAMAGE_TYPE),
        ),
        FatalDamageMessage: MessageContract(
            message_type=FatalDamageMessage,
            param_names=("damage", "target", "source", "card", "damage_type"),
            binder=_bind(_AMOUNT, _TARGET, _SOURCE, _CARD, _DAMAGE_TYPE),
        ),
        PhysicalAttackTakenMessage: MessageContract(
            message_type=PhysicalAttackTakenMessage,
            param_names=("damage", "source", "card", "damage_type"),
            binder=_bind(_AMOUNT, _SOURCE, _CARD, _DAMAGE_TYPE),
        ),
        PhysicalAttackDealtMessage: MessageContract(
            message_type=PhysicalAttackDealtMessage,
            param_names=("damage", "target", "source", "card", "damage_type"),
            binder=_bind(_AMOUNT, _TARGET, _SOURCE, _CARD, _DAMAGE_TYPE),
        ),
        CreatureDiedMessage: MessageContract(
            message_type=CreatureDiedMessage,
            param_names=(),
            binder=_bind(),
        ),
        ShopEnteredMessage: MessageContract(
            message_type=ShopEnteredMessage,
            param_names=(),
            binder=_bind(),
        ),
        EliteVictoryMessage: MessageContract(
            message_type=EliteVictoryMessage,
            param_names=(),
            binder=_bind(),
        ),
    }
    missing = [message_type.__name__ for message_type in EXPLICIT_SUBSCRIPTION_MESSAGE_TYPES if message_type not in contracts]
    if missing:
        raise RuntimeError(f"Missing explicit subscription contracts for: {', '.join(missing)}")
    return contracts


_MESSAGE_CONTRACTS = _build_contracts()


def get_message_contract(message_type: type[GameMessage]) -> MessageContract:
    return _MESSAGE_CONTRACTS[message_type]


def validate_subscription(
    message_type: type[GameMessage],
    param_names: Iterable[str],
    method_name: str | None = None,
) -> bool:
    contract = _MESSAGE_CONTRACTS.get(message_type)
    if contract is None:
        return False
    return contract.supports(param_names, method_name=method_name)


def validate_bound_subscription(bound_method: Callable, message_type: type[GameMessage], method_name: str) -> ParameterNames:
    param_names = subscription_parameter_names(bound_method, bound=True)
    if not validate_subscription(message_type, param_names, method_name=method_name):
        joined_names = ", ".join(param_names)
        raise TypeError(
            f"Unsupported subscription signature for {message_type.__name__}: "
            f"{method_name}({joined_names})"
        )
    return param_names


def invoke_subscription_contract(bound_method: Callable, message: GameMessage, method_name: str | None = None):
    """Invoke a subscriber using its explicit message contract."""
    contract = _MESSAGE_CONTRACTS.get(type(message))
    if contract is None:
        return None
    resolved_method_name = method_name or getattr(bound_method, "__name__", None)
    if resolved_method_name is None:
        return None
    param_names = validate_bound_subscription(bound_method, type(message), resolved_method_name)
    if contract.param_names != param_names:
        return None
    if not contract.predicate(bound_method, message):
        return None
    return contract.binder(bound_method, message)

