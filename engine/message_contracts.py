"""Explicit message subscriber contracts."""
from __future__ import annotations

import inspect
from dataclasses import dataclass, field
from typing import Callable, Iterable, Tuple

from engine.message_helpers import alive_entities_from_game_state
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
    DamageResolvedMessage,
    EliteVictoryMessage,
    GameMessage,
    GoldGainedMessage,
    HealedMessage,
    HpLostMessage,
    PlayerTurnEndedMessage,
    PlayerTurnStartedMessage,
    PotionUsedMessage,
    PowerAppliedMessage,
    RelicObtainedMessage,
    ShuffleMessage,
    ShopEnteredMessage,
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


@dataclass(frozen=True)
class ContractVariant:
    param_names: ParameterNames
    binder: Binder
    predicate: Predicate

    def applies(self, bound_method: Callable, message: GameMessage) -> bool:
        return self.predicate(bound_method, message)

    def invoke(self, bound_method: Callable, message: GameMessage):
        return self.binder(bound_method, message)


@dataclass(frozen=True)
class MessageContract:
    message_type: type[GameMessage]
    default_variants: tuple[ContractVariant, ...] = ()
    method_variants: dict[str, tuple[ContractVariant, ...]] = field(default_factory=dict)

    def variants_for(self, method_name: str | None) -> tuple[ContractVariant, ...]:
        if method_name and method_name in self.method_variants:
            return self.method_variants[method_name]
        return self.default_variants

    def supports(self, param_names: Iterable[str], method_name: str | None = None) -> bool:
        names = tuple(param_names)
        if method_name:
            return any(variant.param_names == names for variant in self.variants_for(method_name))
        if any(variant.param_names == names for variant in self.default_variants):
            return True
        return any(
            variant.param_names == names
            for variants in self.method_variants.values()
            for variant in variants
        )


_ALWAYS: Predicate = lambda _bound_method, _message: True


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


_OWNER = lambda _bound_method, message: message.owner
_ENEMIES = lambda _bound_method, message: message.enemies
_TARGETS = lambda _bound_method, message: message.targets
_FLOOR = lambda _bound_method, message: message.floor
_MESSAGE = lambda _bound_method, message: message
_AMOUNT = lambda _bound_method, message: message.amount
_CARD = lambda _bound_method, message: message.card
_DEST_PILE = lambda _bound_method, message: message.dest_pile
_SOURCE_PILE = lambda _bound_method, message: message.source_pile
_POTION = lambda _bound_method, message: message.potion
_TARGET = lambda _bound_method, message: message.target
_SOURCE = lambda _bound_method, message: message.source
_POWER = lambda _bound_method, message: message.power
_DAMAGE_TYPE = lambda _bound_method, message: message.damage_type
_ENTITIES_FROM_STATE = lambda _bound_method, _message: alive_entities_from_game_state()
_ENTITIES_FROM_MESSAGE = lambda _bound_method, message: message.entities


def _subscriber(bound_method: Callable):
    return getattr(bound_method, "__self__", None)


def _target_has_subscriber_power(bound_method: Callable, message: GameMessage) -> bool:
    target = getattr(message, "target", None)
    powers = getattr(target, "powers", None) or []
    return any(power is _subscriber(bound_method) for power in powers)


def _subscriber_is_target(bound_method: Callable, message: GameMessage) -> bool:
    return _subscriber(bound_method) is getattr(message, "target", None)


def _subscriber_is_source_or_card(bound_method: Callable, message: GameMessage) -> bool:
    return _subscriber(bound_method) in {getattr(message, "source", None), getattr(message, "card", None)}


def _player_available(_bound_method: Callable, _message: GameMessage) -> bool:
    from engine.game_state import game_state

    return game_state.player is not None


def _player_entity(_bound_method: Callable, _message: GameMessage):
    from engine.game_state import game_state

    return game_state.player


def _damage_took_player(_bound_method: Callable, message: GameMessage):
    return getattr(message, "target", None)


def _fatal_target_is_dead(_bound_method: Callable, message: GameMessage) -> bool:
    target = getattr(message, "target", None)
    return bool(getattr(target, "is_dead", lambda: False)())


_VARIANT = lambda names, binder, predicate=_ALWAYS: ContractVariant(tuple(names), binder, predicate)


def _build_contracts() -> dict[type[GameMessage], MessageContract]:
    contracts = {
        CombatStartedMessage: MessageContract(
            message_type=CombatStartedMessage,
            default_variants=(
                _VARIANT(("player", "entities"), _bind(_OWNER, _ENEMIES)),
                _VARIANT(("floor",), _bind(_FLOOR)),
                _VARIANT(("message",), _bind(_MESSAGE)),
                _VARIANT((), _bind()),
            ),
        ),
        CombatEndedMessage: MessageContract(
            message_type=CombatEndedMessage,
            default_variants=(
                _VARIANT(("player", "entities"), _bind(_OWNER, _ENEMIES)),
                _VARIANT(("owner", "entities"), _bind(_OWNER, _ENEMIES)),
                _VARIANT(("message",), _bind(_MESSAGE)),
                _VARIANT((), _bind()),
            ),
        ),
        PlayerTurnStartedMessage: MessageContract(
            message_type=PlayerTurnStartedMessage,
            default_variants=(
                _VARIANT(("player", "entities"), _bind(_OWNER, _ENEMIES)),
                _VARIANT(("message",), _bind(_MESSAGE)),
                _VARIANT((), _bind()),
            ),
        ),
        PlayerTurnEndedMessage: MessageContract(
            message_type=PlayerTurnEndedMessage,
            default_variants=(
                _VARIANT(("player", "entities"), _bind(_OWNER, _ENEMIES)),
                _VARIANT(("message",), _bind(_MESSAGE)),
                _VARIANT((), _bind()),
            ),
        ),
        RelicObtainedMessage: MessageContract(
            message_type=RelicObtainedMessage,
            default_variants=(
                _VARIANT(("message",), _bind(_MESSAGE)),
                _VARIANT((), _bind()),
            ),
        ),
        GoldGainedMessage: MessageContract(
            message_type=GoldGainedMessage,
            default_variants=(
                _VARIANT(("gold_amount", "player"), _bind(_AMOUNT, _OWNER)),
                _VARIANT(("message",), _bind(_MESSAGE)),
                _VARIANT((), _bind()),
            ),
        ),
        ShuffleMessage: MessageContract(
            message_type=ShuffleMessage,
            default_variants=(
                _VARIANT(("message",), _bind(_MESSAGE)),
                _VARIANT((), _bind()),
            ),
        ),
        PotionUsedMessage: MessageContract(
            message_type=PotionUsedMessage,
            default_variants=(
                _VARIANT(("potion", "player", "entities"), _bind(_POTION, _OWNER, _ENTITIES_FROM_MESSAGE)),
                _VARIANT(("potion", "player"), _bind(_POTION, _OWNER)),
                _VARIANT(("message",), _bind(_MESSAGE)),
                _VARIANT((), _bind()),
            ),
        ),
        CardDrawnMessage: MessageContract(
            message_type=CardDrawnMessage,
            default_variants=(
                _VARIANT(("card", "player", "entities"), _bind(_CARD, _OWNER, _ENTITIES_FROM_STATE)),
                _VARIANT(("card",), _bind(_CARD)),
                _VARIANT(("message",), _bind(_MESSAGE)),
                _VARIANT((), _bind()),
            ),
        ),
        CardDiscardedMessage: MessageContract(
            message_type=CardDiscardedMessage,
            default_variants=(
                _VARIANT(("card", "player", "entities"), _bind(_CARD, _OWNER, _ENTITIES_FROM_STATE)),
                _VARIANT(("card",), _bind(_CARD)),
                _VARIANT(("message",), _bind(_MESSAGE)),
                _VARIANT((), _bind()),
            ),
        ),
        CardAddedToPileMessage: MessageContract(
            message_type=CardAddedToPileMessage,
            default_variants=(
                _VARIANT(("card", "dest_pile"), _bind(_CARD, _DEST_PILE)),
                _VARIANT(("card",), _bind(_CARD)),
                _VARIANT(("message",), _bind(_MESSAGE)),
                _VARIANT((), _bind()),
            ),
        ),
        CardExhaustedMessage: MessageContract(
            message_type=CardExhaustedMessage,
            default_variants=(
                _VARIANT(("card", "owner", "source_pile"), _bind(_CARD, _OWNER, _SOURCE_PILE)),
                _VARIANT(("card", "owner"), _bind(_CARD, _OWNER)),
                _VARIANT(("card",), _bind(_CARD)),
                _VARIANT(("message",), _bind(_MESSAGE)),
                _VARIANT((), _bind()),
            ),
        ),
        CardPlayedMessage: MessageContract(
            message_type=CardPlayedMessage,
            default_variants=(
                _VARIANT(("card", "player", "targets"), _bind(_CARD, _OWNER, _TARGETS)),
                _VARIANT(("card",), _bind(_CARD)),
                _VARIANT(("message",), _bind(_MESSAGE)),
                _VARIANT((), _bind()),
            ),
        ),
        AttackPerformedMessage: MessageContract(
            message_type=AttackPerformedMessage,
            default_variants=(
                _VARIANT(("target", "source", "card"), _bind(_TARGET, _SOURCE, _CARD)),
                _VARIANT(("target", "source"), _bind(_TARGET, _SOURCE)),
                _VARIANT(("target",), _bind(_TARGET)),
                _VARIANT(("message",), _bind(_MESSAGE)),
                _VARIANT((), _bind()),
            ),
        ),
        PowerAppliedMessage: MessageContract(
            message_type=PowerAppliedMessage,
            default_variants=(
                _VARIANT(("power", "target", "player", "entities"), _bind(_POWER, _TARGET, _OWNER, _ENTITIES_FROM_MESSAGE)),
                _VARIANT(("power", "owner"), _bind(_POWER, _OWNER)),
                _VARIANT(("power", "source"), _bind(_POWER, _OWNER)),
                _VARIANT(("power", "target"), _bind(_POWER, _TARGET)),
                _VARIANT(("power",), _bind(_POWER)),
                _VARIANT(("message",), _bind(_MESSAGE)),
                _VARIANT((), _bind()),
            ),
        ),
        HealedMessage: MessageContract(
            message_type=HealedMessage,
            default_variants=(
                _VARIANT(("heal_amount", "player", "entities"), _bind_with_previous_hp(_AMOUNT, _TARGET, _ENTITIES_FROM_STATE)),
                _VARIANT(("amount", "player", "entities"), _bind_with_previous_hp(_AMOUNT, _TARGET, _ENTITIES_FROM_STATE)),
                _VARIANT(("amount",), _bind_with_previous_hp(_AMOUNT)),
                _VARIANT(("message",), _bind_with_previous_hp(_MESSAGE)),
                _VARIANT((), _bind_with_previous_hp()),
            ),
        ),
        HpLostMessage: MessageContract(
            message_type=HpLostMessage,
            default_variants=(
                _VARIANT(("amount", "source", "card"), _bind(_AMOUNT, _SOURCE, _CARD)),
                _VARIANT(("amount",), _bind(_AMOUNT)),
                _VARIANT(("message",), _bind(_MESSAGE)),
                _VARIANT((), _bind()),
            ),
        ),
        BlockGainedMessage: MessageContract(
            message_type=BlockGainedMessage,
            default_variants=(
                _VARIANT(("amount", "player", "source", "card"), _bind(_AMOUNT, _TARGET, _SOURCE, _CARD)),
                _VARIANT(("amount", "source", "card"), _bind(_AMOUNT, _SOURCE, _CARD)),
                _VARIANT(("amount",), _bind(_AMOUNT)),
                _VARIANT(("message",), _bind(_MESSAGE)),
                _VARIANT((), _bind()),
            ),
        ),
        DamageResolvedMessage: MessageContract(
            message_type=DamageResolvedMessage,
            method_variants={
                "on_damage_taken": (
                    _VARIANT(
                        ("damage", "source", "card", "player", "damage_type"),
                        _bind(_AMOUNT, _SOURCE, _CARD, _damage_took_player, _DAMAGE_TYPE),
                        _target_has_subscriber_power,
                    ),
                    _VARIANT(
                        ("amount", "source", "card", "player", "damage_type"),
                        _bind(_AMOUNT, _SOURCE, _CARD, _damage_took_player, _DAMAGE_TYPE),
                        _target_has_subscriber_power,
                    ),
                    _VARIANT(
                        ("damage", "source", "card", "damage_type"),
                        _bind(_AMOUNT, _SOURCE, _CARD, _DAMAGE_TYPE),
                        _subscriber_is_target,
                    ),
                    _VARIANT(
                        ("amount", "source", "card", "damage_type"),
                        _bind(_AMOUNT, _SOURCE, _CARD, _DAMAGE_TYPE),
                        _subscriber_is_target,
                    ),
                    _VARIANT(
                        ("damage",),
                        _bind(_AMOUNT),
                        _subscriber_is_target,
                    ),
                    _VARIANT(
                        ("amount",),
                        _bind(_AMOUNT),
                        _subscriber_is_target,
                    ),
                    _VARIANT(
                        ("damage", "source", "player", "entities"),
                        _bind(_AMOUNT, _SOURCE, _player_entity, _ENTITIES_FROM_STATE),
                        _player_available,
                    ),
                ),
                "on_damage_dealt": (
                    _VARIANT(("damage", "target", "source", "card"), _bind(_AMOUNT, _TARGET, _SOURCE, _CARD)),
                    _VARIANT(
                        ("damage", "target", "card", "damage_type"),
                        _bind(_AMOUNT, _TARGET, _CARD, _DAMAGE_TYPE),
                        _subscriber_is_source_or_card,
                    ),
                    _VARIANT(
                        ("damage", "target"),
                        _bind(_AMOUNT, _TARGET),
                        _subscriber_is_source_or_card,
                    ),
                    _VARIANT(
                        ("damage", "target", "player", "entities"),
                        _bind(_AMOUNT, _TARGET, _player_entity, _ENTITIES_FROM_STATE),
                        _player_available,
                    ),
                ),
                "on_fatal": (
                    _VARIANT(
                        ("damage", "target", "card", "damage_type"),
                        _bind(_AMOUNT, _TARGET, _CARD, _DAMAGE_TYPE),
                        _fatal_target_is_dead,
                    ),
                    _VARIANT(("message",), _bind(_MESSAGE), _fatal_target_is_dead),
                    _VARIANT((), _bind(), _fatal_target_is_dead),
                ),
            },
        ),
        CreatureDiedMessage: MessageContract(
            message_type=CreatureDiedMessage,
            default_variants=(
                _VARIANT(("message",), _bind(_MESSAGE)),
                _VARIANT((), _bind()),
            ),
        ),
        ShopEnteredMessage: MessageContract(
            message_type=ShopEnteredMessage,
            default_variants=(
                _VARIANT(("player", "entities"), _bind(_OWNER, _ENTITIES_FROM_MESSAGE)),
                _VARIANT(("owner", "entities"), _bind(_OWNER, _ENTITIES_FROM_MESSAGE)),
                _VARIANT(("player",), _bind(_OWNER)),
                _VARIANT(("owner",), _bind(_OWNER)),
                _VARIANT(("message",), _bind(_MESSAGE)),
                _VARIANT((), _bind()),
            ),
        ),
        EliteVictoryMessage: MessageContract(
            message_type=EliteVictoryMessage,
            default_variants=(
                _VARIANT(("player", "entities"), _bind(_OWNER, _ENTITIES_FROM_MESSAGE)),
                _VARIANT(("owner", "entities"), _bind(_OWNER, _ENTITIES_FROM_MESSAGE)),
                _VARIANT(("player",), _bind(_OWNER)),
                _VARIANT(("owner",), _bind(_OWNER)),
                _VARIANT(("message",), _bind(_MESSAGE)),
                _VARIANT((), _bind()),
            ),
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
    for variant in contract.variants_for(resolved_method_name):
        if variant.param_names != param_names:
            continue
        if not variant.applies(bound_method, message):
            continue
        return variant.invoke(bound_method, message)
    return None

