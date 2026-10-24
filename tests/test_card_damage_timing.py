"""Original card damage snapshots versus per-hit random recalculation.

All card cases enter through PlayCardAction. Patched random.choice supplies
controlled targeting inputs; it does not replace damage or queue execution.
"""

import random

import pytest

from actions.combat_cards import AttackAction, PlayCardAction
from actions.combat_damage import DealDamageAction
from cards.defect.barrage import Barrage
from cards.defect.rip_and_tear import RipAndTear
from cards.defect.thunder_strike import ThunderStrike
from cards.ironclad.pummel import Pummel
from cards.ironclad.fiend_fire import FiendFire
from cards.ironclad.strike import Strike
from cards.ironclad.sword_boomerang import SwordBoomerang
from cards.ironclad.twin_strike import TwinStrike
from cards.ironclad.whirlwind import Whirlwind
from cards.silent.dagger_spray import DaggerSpray
from cards.silent.riddle_with_holes import RiddleWithHoles
from cards.silent.skewer import Skewer
from cards.watcher.ragnarok import Ragnarok
from enemies.act1.cultist import Cultist
from enemies.act3.awakened_one import AwakenedOne
from engine.messages import DamageDealtMessage
from orbs.lightning import LightningOrb
from powers.definitions.buffer import BufferPower
from powers.definitions.beat_of_death import BeatOfDeathPower
from powers.definitions.choke import ChokePower
from powers.definitions.flying import FlyingPower
from powers.definitions.intangible import IntangiblePower
from powers.definitions.invincible import InvinciblePower
from powers.definitions.pen_nib import PenNibPower
from powers.definitions.strength import StrengthPower
from powers.definitions.slow import SlowPower
from powers.definitions.thorns import ThornsPower
from powers.definitions.time_warp import TimeWarpPower
from powers.definitions.vulnerable import VulnerablePower
from powers.definitions.vigor import VigorPower
from powers.definitions.weak import WeakPower
from relics.character.ironclad import RedSkull
from tests.test_combat_utils import create_test_helper
from utils.types import DamageType


FIXED_CARDS = [Pummel, RiddleWithHoles, TwinStrike, DaggerSpray,
               Skewer, Whirlwind, Barrage]
RANDOM_CARDS = [SwordBoomerang, Ragnarok, RipAndTear, ThunderStrike]


def setup_card(card_class, *, hp=54, enemies=None):
    helper = create_test_helper()
    player = helper.create_player(max_hp=100, hp=hp, energy=4)
    player.base_draw_count = 0
    player.relics.append(RedSkull())
    enemies = enemies if enemies is not None else [Cultist()]
    for enemy in enemies:
        enemy._max_hp = 500
        enemy.hp = 500
    combat = helper.start_combat(enemies)
    card = card_class()
    if card_class is Barrage:
        player.orb_manager.max_orb_slots = 4
        player.orb_manager.orbs.extend(LightningOrb() for _ in range(4))
    if card_class is ThunderStrike:
        combat.combat_state.orb_history["Lightning"] = 4
    helper.add_card_to_hand(card)
    return helper, player, card, enemies


def trace_card_hits(helper, player, card, monkeypatch, after_hit=None):
    hits = []
    original = helper.game_state.publish_message

    def publish(message, *args, **kwargs):
        result = original(message, *args, **kwargs)
        if isinstance(message, DamageDealtMessage) and message.card is card:
            strength = player.get_power("Strength")
            hits.append((message.target, message.amount,
                         strength.amount if strength is not None else 0))
            if after_hit is not None:
                after_hit(len(hits))
        return result

    monkeypatch.setattr(helper.game_state, "publish_message", publish)
    return hits


def play(helper, card):
    # Auto targeting avoids the input UI while retaining normal costs,
    # card.on_play, action queue, hooks and card disposal.
    helper.game_state.add_action(PlayCardAction(card, is_auto=True))
    assert helper.game_state.drive_actions() is None


@pytest.mark.parametrize("card_class", FIXED_CARDS)
@pytest.mark.parametrize("upgraded", [False, True])
def test_fixed_multihit_keeps_damage_when_red_skull_activates(
        card_class, upgraded, monkeypatch):
    helper, player, card, enemies = setup_card(card_class, hp=51)
    if upgraded:
        card.upgrade()
    enemies[0].add_power(ThornsPower(amount=3, owner=enemies[0]))
    hits = trace_card_hits(helper, player, card, monkeypatch)

    play(helper, card)

    assert len(hits) == (4 if card_class is Skewer else card.attack_times)
    assert [damage for _, damage, _ in hits] == [card.damage] * len(hits)
    assert [strength for _, _, strength in hits] == [0] + [3] * (len(hits) - 1)
    strength = player.get_power("Strength")
    assert strength is not None and strength.amount == 3


@pytest.mark.parametrize("card_class", RANDOM_CARDS)
def test_random_multihit_recalculates_after_real_red_skull_activation(
        card_class, monkeypatch):
    helper, player, card, enemies = setup_card(card_class, hp=51)
    enemies[0].add_power(ThornsPower(amount=3, owner=enemies[0]))
    hits = trace_card_hits(helper, player, card, monkeypatch)

    play(helper, card)

    assert len(hits) == card.attack_times
    assert [damage for _, damage, _ in hits] == [card.damage] + [card.damage + 3] * (len(hits) - 1)
    assert [strength for _, _, strength in hits] == [0] + [3] * (len(hits) - 1)


@pytest.mark.parametrize("card_class", RANDOM_CARDS)
def test_random_multihit_chooses_only_current_living_targets_once_per_hit(
        card_class, monkeypatch):
    helper, player, card, enemies = setup_card(
        card_class, enemies=[Cultist(), Cultist(), AwakenedOne()])
    first, survivor, half_dead = enemies
    first.hp = 1
    half_dead.hp = 0
    assert half_dead.half_dead
    choices = []

    def choose(candidates):
        # Controlled RNG: choose the first eligible enemy on each actual hit.
        choices.append(tuple(candidates))
        return candidates[0]

    monkeypatch.setattr(random, "choice", choose)
    hits = trace_card_hits(helper, player, card, monkeypatch)

    play(helper, card)

    assert len(choices) == card.attack_times
    assert choices[0] == (first, survivor)
    assert choices[1:] == [(survivor,)] * (card.attack_times - 1)
    assert [target for target, _, _ in hits] == [first] + [survivor] * (card.attack_times - 1)


@pytest.mark.parametrize("card_class", RANDOM_CARDS)
def test_random_multihit_recalculates_vulnerability_for_each_selected_target(
        card_class, monkeypatch):
    helper, player, card, enemies = setup_card(
        card_class, enemies=[Cultist(), Cultist()])
    normal, vulnerable = enemies
    vulnerable.add_power(VulnerablePower(amount=2, owner=vulnerable))
    choices = []

    def choose(candidates):
        target = candidates[len(choices) % 2]
        choices.append(target)
        return target

    monkeypatch.setattr(random, "choice", choose)
    hits = trace_card_hits(helper, player, card, monkeypatch)

    play(helper, card)

    assert len(choices) == card.attack_times
    assert [target for target, _, _ in hits] == choices
    assert [damage for _, damage, _ in hits] == [
        int(card.damage * (1.5 if target is vulnerable else 1)) for target in choices]


@pytest.mark.parametrize("defense", ["block", "buffer", "invincible"])
def test_fixed_card_preserves_live_defense_consumption(defense, monkeypatch):
    helper, player, card, enemies = setup_card(RiddleWithHoles)
    enemy = enemies[0]
    if defense == "block":
        enemy.block = 4
        expected = [0, 2, 3, 3, 3]
    elif defense == "buffer":
        enemy.add_power(BufferPower(amount=1, owner=enemy))
        # Buffer returns before publishing DamageDealtMessage.
        expected = [3, 3, 3, 3]
    else:
        enemy.add_power(InvinciblePower(amount=7, owner=enemy))
        expected = [3, 3, 1, 0, 0]
    hits = trace_card_hits(helper, player, card, monkeypatch)

    play(helper, card)

    assert [damage for _, damage, _ in hits] == expected
    assert enemy.hp == 500 - sum(expected)
    if defense == "buffer":
        assert enemy.get_power("Buffer") is None


@pytest.mark.parametrize("card_class", [RiddleWithHoles, RipAndTear])
def test_enemy_intangible_added_midcard_only_affects_recalculated_hits(
        card_class, monkeypatch):
    helper, player, card, enemies = setup_card(card_class)
    enemy = enemies[0]

    def add_intangible(hit_count):
        if hit_count == 1:
            enemy.add_power(IntangiblePower(amount=1, owner=enemy))

    hits = trace_card_hits(helper, player, card, monkeypatch, add_intangible)

    play(helper, card)

    subsequent = card.damage if card_class is RiddleWithHoles else 1
    assert [damage for _, damage, _ in hits] == [card.damage] + [subsequent] * (len(hits) - 1)


@pytest.mark.parametrize("card_class", [RiddleWithHoles, RipAndTear])
def test_strength_removed_midcard_only_affects_recalculated_hits(
        card_class, monkeypatch):
    helper, player, card, _ = setup_card(card_class)
    strength = StrengthPower(amount=3, owner=player)
    player.add_power(strength)

    def remove_strength(hit_count):
        if hit_count == 1:
            # Controlled power-state change isolates the card snapshot contract.
            strength.amount = 0

    hits = trace_card_hits(helper, player, card, monkeypatch, remove_strength)

    play(helper, card)

    subsequent = card.damage + 3 if card_class is RiddleWithHoles else card.damage
    assert [damage for _, damage, _ in hits] == [card.damage + 3] + [subsequent] * (len(hits) - 1)


@pytest.mark.parametrize("card_class", [RiddleWithHoles, RipAndTear])
def test_flying_exhaustion_during_card_only_affects_recalculated_hits(
        card_class, monkeypatch):
    helper, player, card, enemies = setup_card(card_class)
    flying = FlyingPower(amount=1, owner=enemies[0])
    enemies[0].add_power(flying)
    hits = trace_card_hits(helper, player, card, monkeypatch)

    play(helper, card)

    first = card.damage // 2
    subsequent = first if card_class is RiddleWithHoles else card.damage
    assert [damage for _, damage, _ in hits] == [first] + [subsequent] * (len(hits) - 1)
    assert flying.amount == 0


@pytest.mark.parametrize("card_class", [RiddleWithHoles, RipAndTear])
def test_strength_weak_vulnerability_are_applied_once_with_final_floor(
        card_class, monkeypatch):
    helper, player, card, enemies = setup_card(card_class)
    player.add_power(StrengthPower(amount=2, owner=player))
    player.add_power(WeakPower(amount=2, owner=player))
    enemies[0].add_power(VulnerablePower(amount=2, owner=enemies[0]))
    hits = trace_card_hits(helper, player, card, monkeypatch)

    play(helper, card)

    # Riddle: floor((3+2)*.75*1.5)=5, not an intermediate floor of 4.
    expected = int((card.damage + 2) * 0.75 * 1.5)
    assert [damage for _, damage, _ in hits] == [expected] * card.attack_times


@pytest.mark.parametrize("upgraded", [False, True])
def test_fiend_fire_uses_card_snapshot_and_attributes_all_exhaust_hits(
        upgraded, monkeypatch):
    helper, player, card, enemies = setup_card(FiendFire, hp=51)
    if upgraded:
        card.upgrade()
    fuel = [Strike() for _ in range(3)]
    for item in fuel:
        helper.add_card_to_hand(item)
    enemies[0].add_power(ThornsPower(amount=3, owner=enemies[0]))
    hits = trace_card_hits(helper, player, card, monkeypatch)

    play(helper, card)

    assert [damage for _, damage, _ in hits] == [10 if upgraded else 7] * 3
    assert [strength for _, _, strength in hits] == [0, 3, 3]
    exhausted = player.card_manager.get_pile("exhaust_pile")
    assert exhausted is not None
    assert all(item in exhausted for item in [card, *fuel])


@pytest.mark.parametrize("card_class", [RiddleWithHoles, RipAndTear])
@pytest.mark.parametrize("boost", ["pen_nib", "vigor"])
def test_next_attack_boost_applies_to_every_hit_once(card_class, boost, monkeypatch):
    helper, player, card, _ = setup_card(card_class)
    if boost == "pen_nib":
        player.add_power(PenNibPower(amount=1, owner=player))
        expected = card.damage * 2
        power_name = "PenNib"
    else:
        player.add_power(VigorPower(amount=4, owner=player))
        expected = card.damage + 4
        power_name = "Vigor"
    hits = trace_card_hits(helper, player, card, monkeypatch)

    play(helper, card)

    assert [damage for _, damage, _ in hits] == [expected] * card.attack_times
    assert player.get_power(power_name) is None


@pytest.mark.parametrize("action_class", [AttackAction, DealDamageAction])
def test_legacy_queued_action_without_snapshot_field_uses_live_damage(action_class):
    helper, player, card, enemies = setup_card(Strike)
    action = action_class(6, target=enemies[0], source=player,
                          damage_type=DamageType.PHYSICAL, card=card)
    # Old serialized queues have the raw six damage and lack this new field.
    del action.damage_is_calculated
    player.add_power(StrengthPower(amount=3, owner=player))
    helper.game_state.add_action(action)

    assert helper.game_state.drive_actions() is None

    assert enemies[0].hp == 491


@pytest.mark.parametrize("card_class", RANDOM_CARDS)
@pytest.mark.parametrize("power_class", [SlowPower, ChokePower,
                                         BeatOfDeathPower, TimeWarpPower])
def test_random_card_notifies_every_enemy_card_listener_once(
        card_class, power_class, monkeypatch):
    helper, player, card, enemies = setup_card(
        card_class, hp=100, enemies=[Cultist(), Cultist()])
    amount = 0 if power_class in (SlowPower, TimeWarpPower) else 2
    powers = [power_class(amount=amount, owner=enemy) for enemy in enemies]
    for enemy, power in zip(enemies, powers):
        enemy.add_power(power)
    # Controlled RNG sends all attacks to the first enemy. The second enemy
    # must still receive the card-play notification despite never being hit.
    choices = []

    def choose(candidates):
        choices.append(tuple(candidates))
        return candidates[0]

    monkeypatch.setattr(random, "choice", choose)
    messages = []
    original = helper.game_state.publish_message

    def publish(message, *args, **kwargs):
        messages.append(message)
        return original(message, *args, **kwargs)

    monkeypatch.setattr(helper.game_state, "publish_message", publish)

    play(helper, card)

    assert len(choices) == card.attack_times
    if power_class is SlowPower:
        # The pre-existing Slow trigger-order discrepancy is outside scope;
        # this asserts notification counts, not damage-equivalence timing.
        assert [power.amount for power in powers] == [1, 1]
    elif power_class is TimeWarpPower:
        assert [power.counter for power in powers] == [1, 1]
    elif power_class is BeatOfDeathPower:
        reactions = [message for message in messages
                     if isinstance(message, DamageDealtMessage)
                     and message.target is player]
        assert [message.source for message in reactions] == enemies
        assert [message.amount for message in reactions] == [2, 2]
        assert player.hp == 96
    else:
        reactions = [message for message in messages
                     if isinstance(message, DamageDealtMessage)
                     and message.damage_type == DamageType.MAGICAL]
        assert [message.target for message in reactions] == enemies
        assert [message.amount for message in reactions] == [2, 2]
