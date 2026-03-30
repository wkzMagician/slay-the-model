import pytest

from enemies.base import Enemy
from engine.message_bus import MessageBus
from engine.message_contracts import get_message_contract, validate_subscription
from engine.messages import (
    EXPLICIT_SUBSCRIPTION_MESSAGE_TYPES,
    CardPlayedMessage,
    CardDrawnMessage,
    CombatStartedMessage,
    DamageResolvedMessage,
)
from engine.subscriptions import subscribe


class _BrokenDamageEnemy(Enemy):
    def __init__(self):
        super().__init__(hp_range=(10, 10))

    def on_damage_taken(self, damage, unexpected, extra):
        return []


def test_invalid_subscription_signature_raises():
    with pytest.raises(TypeError):
        @subscribe(CardDrawnMessage)
        def bad_handler(self, a, b, c, d):
            return []



def test_keyword_only_subscription_signature_raises():
    with pytest.raises(TypeError):
        @subscribe(CardDrawnMessage)
        def keyword_only_handler(self, *, message):
            return []



def test_inherited_invalid_override_signature_raises_during_dispatch():
    enemy = _BrokenDamageEnemy()
    bus = MessageBus()

    with pytest.raises(TypeError, match="Unsupported subscription signature"):
        bus.publish(
            DamageResolvedMessage(amount=5, target=enemy, source=None, card=None, damage_type="attack"),
            participants=[enemy],
        )



def test_card_drawn_contract_accepts_message_form():
    assert validate_subscription(CardDrawnMessage, ["message"]) is True



def test_combat_started_contract_accepts_floor_form():
    assert validate_subscription(CombatStartedMessage, ["floor"]) is True



def test_contract_registry_exposes_declared_variants():
    contract = get_message_contract(CardDrawnMessage)

    assert contract.message_type is CardDrawnMessage
    assert ("message",) in {variant.param_names for variant in contract.default_variants}
    assert ("card", "player", "entities") in {variant.param_names for variant in contract.default_variants}


def test_card_played_contract_uses_targets_form():
    card_play_contract = get_message_contract(CardPlayedMessage)
    assert ("card", "player", "targets") in {variant.param_names for variant in card_play_contract.default_variants}



def test_messages_export_explicit_subscription_scope():
    assert CardDrawnMessage in EXPLICIT_SUBSCRIPTION_MESSAGE_TYPES
    assert CombatStartedMessage in EXPLICIT_SUBSCRIPTION_MESSAGE_TYPES
