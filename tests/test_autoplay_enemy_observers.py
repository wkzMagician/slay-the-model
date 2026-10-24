"""PWR-030: enemy observers receive each player play irrespective of its target.

This verifies delivery, not complete Slow or Time Warp behavior. In particular,
their preexisting damage timing and Time Warp's Strength amount are out of scope.
The manual-only cases also run against the pre-fix parent for before evidence.
"""

import pytest

from actions.combat_cards import PlayCardAction
from actions.combat_status import UsePotionAction
from cards.ironclad.defend import Defend
from cards.ironclad.strike import Strike
from enemies.act1.cultist import Cultist
from engine.messages import CardPlayedMessage, DamageDealtMessage
from potions.global_potions import DistilledChaos
from powers.definitions.beat_of_death import BeatOfDeathPower
from powers.definitions.choke import ChokePower
from powers.definitions.echo_form import EchoFormPower
from powers.definitions.slow import SlowPower
from powers.definitions.time_warp import TimeWarpPower
from tests.test_combat_utils import create_test_helper


POWER_TYPES = [SlowPower, ChokePower, BeatOfDeathPower, TimeWarpPower]


def prepare(monkeypatch, enemy_count=1):
    helper = create_test_helper()
    player = helper.create_player(hp=100, max_hp=100, energy=10)
    player.base_draw_count = 0
    enemies = [Cultist() for _ in range(enemy_count)]
    for enemy in enemies:
        enemy._max_hp = 1000
        enemy.hp = 1000
    combat = helper.start_combat(enemies)
    assert helper.game_state.drive_actions() is None
    messages = []
    original = helper.game_state.publish_message

    def publish(message, *args, **kwargs):
        messages.append(message)
        return original(message, *args, **kwargs)

    monkeypatch.setattr(helper.game_state, "publish_message", publish)
    return helper, player, enemies, combat, messages


def attach(enemy, power_type):
    amount = 0 if power_type in (SlowPower, TimeWarpPower) else 1
    power = power_type(amount=amount, owner=enemy)
    enemy.add_power(power)
    return power


def play(helper, card):
    helper.add_card_to_hand(card)
    helper.game_state.add_action(PlayCardAction(card))
    assert helper.game_state.drive_actions() is None


def use_chaos(helper):
    item = DistilledChaos()
    player = helper.game_state.player
    player.potions.append(item)
    helper.game_state.add_action(UsePotionAction(item, target=player))
    assert helper.game_state.drive_actions() is None


def assert_observed(power, count, enemy, player, messages):
    if isinstance(power, SlowPower):
        assert power.amount == count
    elif isinstance(power, TimeWarpPower):
        assert power.card_counter == count
    elif isinstance(power, ChokePower):
        assert enemy.hp == 1000 - count
    else:
        hits = [message for message in messages
                if isinstance(message, DamageDealtMessage)
                and message.source is enemy and message.target is player]
        assert len(hits) == count


@pytest.mark.parametrize("power_type", POWER_TYPES)
@pytest.mark.parametrize("entry", ["manual", "chaos", "echo_manual", "echo_chaos"])
def test_enemy_observes_each_self_target_play_once(power_type, entry, monkeypatch):
    helper, player, enemies, combat, messages = prepare(monkeypatch)
    enemy = enemies[0]
    power = attach(enemy, power_type)
    if entry.startswith("echo_"):
        player.add_power(EchoFormPower(amount=1, owner=player))
    card = Defend()
    if entry.endswith("chaos"):
        helper.add_card_to_draw_pile(card)
        use_chaos(helper)
    else:
        play(helper, card)
    expected = 2 if entry.startswith("echo_") else 1
    played = [message.card for message in messages if isinstance(message, CardPlayedMessage)]
    assert len(played) == expected and played[0] is card
    if expected == 2:
        assert played[1] is not card
    assert combat.combat_state.turn_cards_played == expected
    assert_observed(power, expected, enemy, player, messages)
    assert player.block == expected * (4 if power_type is BeatOfDeathPower else 5)
    assert player.hp == 100


@pytest.mark.parametrize("power_type", POWER_TYPES)
def test_targeted_and_untargeted_enemies_each_observe_attack_once(power_type, monkeypatch):
    helper, player, enemies, _, messages = prepare(monkeypatch, enemy_count=2)
    powers = [attach(enemy, power_type) for enemy in enemies]
    play(helper, Strike())
    played = [message for message in messages if isinstance(message, CardPlayedMessage)]
    assert len(played) == 1
    targeted = played[0].targets
    assert targeted == [enemies[0]]
    for power, enemy in zip(powers, enemies):
        if isinstance(power, ChokePower):
            # Keep the delivery assertion separate from the Strike's damage.
            hits = [message for message in messages
                    if isinstance(message, DamageDealtMessage)
                    and message.target is enemy and message.amount == 1]
            assert len(hits) == 1
        else:
            assert_observed(power, 1, enemy, player, messages)


def test_time_warp_twelfth_self_target_autoplay_keeps_effect_and_cancels_pending(monkeypatch):
    helper, player, enemies, combat, messages = prepare(monkeypatch)
    power = TimeWarpPower(amount=11, owner=enemies[0])
    enemies[0].add_power(power)
    cards = [Defend(), Defend(), Defend()]
    player.card_manager.piles["draw_pile"] = cards.copy()
    use_chaos(helper)
    played = [message.card for message in messages if isinstance(message, CardPlayedMessage)]
    assert played == [cards[-1]]
    assert power.card_counter == 0
    assert combat.combat_state.current_phase == "player_end"
    assert combat.combat_state.turn_cards_played == 1
    assert player.block == 5
    assert all(player.card_manager.get_card_location(card) == "discard_pile" for card in cards)
    assert not helper.game_state.pending_card_plays
    assert not helper.game_state.active_card_plays
