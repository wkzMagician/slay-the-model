"""Real-entry regressions for replay/autoplay lifecycles (PWR-010/011/012).

Expectations follow the original GameActionManager card queue and UseCardAction:
effects finish before the next play; cancelled autoplay still receives cleanup.
"""

import pytest

from actions.combat_cards import PlayCardAction
from actions.combat_status import UsePotionAction
from cards.colorless.wound import Wound
from cards.ironclad.clash import Clash
from cards.ironclad.bash import Bash
from cards.ironclad.defend import Defend
from cards.ironclad.entrench import Entrench
from cards.ironclad.havoc import Havoc
from cards.ironclad.inflame import Inflame
from cards.ironclad.pummel import Pummel
from cards.ironclad.strike import Strike
from cards.ironclad.whirlwind import Whirlwind
from cards.silent.grand_finale import GrandFinale
from cards.watcher.conclude import Conclude
from cards.watcher.omniscience import Omniscience
from enemies.act1.cultist import Cultist
from engine.messages import CardExhaustedMessage, CardPlayedMessage, DamageDealtMessage
from potions.global_potions import DistilledChaos, DuplicationPotion
from powers.definitions.amplify import AmplifyPower
from powers.definitions.burst import BurstPower
from powers.definitions.double_tap import DoubleTapPower
from powers.definitions.echo_form import EchoFormPower
from powers.definitions.mayhem import MayhemPower
from powers.definitions.vigor import VigorPower
from relics.global_relics.boss import SacredBark
from relics.global_relics.common import PenNib
from relics.global_relics.event import Necronomicon
from tests.test_combat_utils import create_test_helper


def prepare(monkeypatch, energy=3):
    helper = create_test_helper()
    player = helper.create_player(hp=100, max_hp=100, energy=energy)
    player.base_draw_count = 0
    enemy = Cultist()
    enemy._max_hp = 1000
    enemy.hp = 1000
    combat = helper.start_combat([enemy])
    assert helper.game_state.drive_actions() is None
    messages = []
    original = helper.game_state.publish_message

    def publish(message, *args, **kwargs):
        messages.append((message, enemy.hp, player.block))
        return original(message, *args, **kwargs)

    monkeypatch.setattr(helper.game_state, "publish_message", publish)
    return helper, player, enemy, combat, messages


def play(helper, card):
    helper.add_card_to_hand(card)
    helper.game_state.add_action(PlayCardAction(card))
    return helper.game_state.drive_actions()


def potion(helper, item):
    helper.game_state.player.potions.append(item)
    helper.game_state.add_action(UsePotionAction(item, target=helper.game_state.player))
    return helper.game_state.drive_actions()


def played(messages):
    return [message.card for message, _, _ in messages if isinstance(message, CardPlayedMessage)]


def battle_cards(player):
    return [card for pile, cards in player.card_manager.piles.items() if pile != "deck" for card in cards]


@pytest.mark.parametrize("source,card_type,effect", [
    ("echo", Strike, "attack"), ("double", Strike, "attack"),
    ("burst", Defend, "block"), ("amplify", Inflame, "strength"),
    ("potion", Strike, "attack"), ("necronomicon", Whirlwind, "x_attack"),
])
def test_replay_is_independent_counted_play_without_extra_cost_or_permanent_copy(source, card_type, effect, monkeypatch):
    helper, player, enemy, combat, messages = prepare(monkeypatch)
    nib = PenNib()
    player.relics.append(nib)
    powers = {"echo": EchoFormPower, "double": DoubleTapPower, "burst": BurstPower, "amplify": AmplifyPower}
    if source in powers:
        player.add_power(powers[source](amount=1, owner=player))
    elif source == "potion":
        assert potion(helper, DuplicationPotion()) is None
    else:
        player.relics.append(Necronomicon())
    card = card_type()
    assert play(helper, card) is None
    cards = played(messages)
    assert len(cards) == 2
    assert cards[0] is card and cards[1] is not card
    assert cards[1].idstr == card.idstr
    assert combat.combat_state.turn_cards_played == 2
    assert player.energy == (0 if effect == "x_attack" else 2)
    assert battle_cards(player) == ([] if effect == "strength" else [card])
    if effect in ("attack", "x_attack"):
        assert combat.combat_state.turn_attack_cards_played == 2
        assert nib.attacks_played == 2
        assert enemy.hp == (970 if effect == "x_attack" else 988)
    elif effect == "block":
        assert player.block == 10
    else:
        assert player.strength == 4
        assert combat.combat_state.power_cards_played == 2


def test_distilled_chaos_keeps_three_original_defends_in_discard(monkeypatch):
    helper, player, _, combat, messages = prepare(monkeypatch, energy=0)
    cards = [Defend() for _ in range(3)]
    player.card_manager.piles["draw_pile"] = cards.copy()
    assert potion(helper, DistilledChaos()) is None
    assert player.block == 15
    assert player.energy == 0
    assert combat.combat_state.turn_cards_played == 3
    assert set(map(id, played(messages))) == set(map(id, cards))
    assert set(map(id, player.card_manager.piles["discard_pile"])) == set(map(id, cards))
    assert len(battle_cards(player)) == 3


@pytest.mark.parametrize("card_type", [Wound, Clash, GrandFinale])
def test_mayhem_cancelled_card_discards_without_play_event(card_type, monkeypatch):
    helper, player, enemy, combat, messages = prepare(monkeypatch, energy=0)
    card = card_type()
    blocker = Defend()
    helper.add_card_to_hand(blocker)
    player.card_manager.piles["draw_pile"] = [Defend(), card]
    power = MayhemPower(owner=player)
    player.add_power(power)
    power.on_turn_start()
    assert helper.game_state.drive_actions() is None
    assert player.card_manager.get_card_location(card) == "discard_pile"
    assert player.card_manager.get_card_location(blocker) == "hand"
    assert not played(messages)
    assert combat.combat_state.turn_cards_played == 0
    assert enemy.hp == 1000


@pytest.mark.parametrize("card_type", [Wound, Clash, GrandFinale])
def test_failed_manual_play_keeps_card_in_hand(card_type, monkeypatch):
    helper, player, _, combat, messages = prepare(monkeypatch)
    helper.add_card_to_hand(Defend())
    helper.add_card_to_draw_pile(Defend())
    card = card_type()
    assert play(helper, card) is None
    assert player.card_manager.get_card_location(card) == "hand"
    assert combat.combat_state.turn_cards_played == 0
    assert not played(messages)


@pytest.mark.parametrize("card_type,damage", [(Strike, 6), (GrandFinale, 50)])
def test_havoc_removes_card_before_validation_and_exhausts_once(card_type, damage, monkeypatch):
    helper, player, enemy, combat, messages = prepare(monkeypatch)
    card = card_type()
    helper.add_card_to_draw_pile(card)
    assert play(helper, Havoc()) is None
    assert enemy.hp == 1000 - damage
    assert player.energy == 2
    assert player.card_manager.get_card_location(card) == "exhaust_pile"
    assert sum(item is card for item in battle_cards(player)) == 1
    assert combat.combat_state.turn_cards_played == 2
    assert played(messages)[1] is card


def test_distilled_chaos_finishes_first_effect_before_next_card_event(monkeypatch):
    helper, player, _, _, messages = prepare(monkeypatch)
    first, second, third = Strike(), Strike(), Defend()
    player.card_manager.piles["draw_pile"] = [third, second, first]
    assert potion(helper, DistilledChaos()) is None
    snapshots = [(m.card, hp, block) for m, hp, block in messages if isinstance(m, CardPlayedMessage)]
    assert [card for card, _, _ in snapshots] == [first, second, third]
    assert [hp for _, hp, _ in snapshots] == [1000, 994, 988]


def test_conclude_cancels_remaining_chaos_plays_but_cleans_up_cards(monkeypatch):
    helper, player, enemy, combat, messages = prepare(monkeypatch, energy=0)
    first, second, third = Conclude(), Defend(), Defend()
    player.card_manager.piles["draw_pile"] = [third, second, first]
    assert potion(helper, DistilledChaos()) is None
    assert played(messages) == [first]
    assert enemy.hp == 988
    assert player.block == 0
    assert combat.combat_state.turn_cards_played == 1
    assert all(player.card_manager.get_card_location(card) == "discard_pile" for card in [first, second, third])


def test_distilled_chaos_unplayable_wound_still_discards(monkeypatch):
    helper, player, _, combat, messages = prepare(monkeypatch)
    wound = Wound()
    helper.add_card_to_draw_pile(wound)
    assert potion(helper, DistilledChaos()) is None
    assert player.card_manager.get_card_location(wound) == "discard_pile"
    assert not played(messages)
    assert combat.combat_state.turn_cards_played == 0


@pytest.mark.parametrize("power_type", [EchoFormPower, DoubleTapPower])
@pytest.mark.parametrize("upgraded", [False, True])
def test_replay_preserves_upgrade_and_consumes_vigor_on_first_play_only(power_type, upgraded, monkeypatch):
    helper, player, enemy, _, messages = prepare(monkeypatch)
    player.add_power(power_type(amount=1, owner=player))
    player.add_power(VigorPower(amount=4, owner=player))
    card = Strike()
    if upgraded:
        card.upgrade()
    assert play(helper, card) is None
    expected = 9 if upgraded else 6
    damages = [message.amount for message, _, _ in messages if isinstance(message, DamageDealtMessage) and message.target is enemy]
    assert damages == [expected + 4, expected]
    assert len(played(messages)) == 2
    assert played(messages)[1].damage == expected
    assert player.get_power("Vigor") is None


@pytest.mark.parametrize("initial_counter,damage,final_counter", [(8, 18, 0), (9, 18, 1)])
def test_echo_replay_runs_pen_nib_hooks_between_plays(initial_counter, damage, final_counter, monkeypatch):
    helper, player, enemy, _, messages = prepare(monkeypatch)
    nib = PenNib()
    nib.attacks_played = initial_counter
    player.relics.append(nib)
    if initial_counter == 9:
        nib.on_combat_start(1)
        assert helper.game_state.drive_actions() is None
    player.add_power(EchoFormPower(amount=1, owner=player))
    assert play(helper, Strike()) is None
    assert enemy.hp == 1000 - damage
    assert nib.attacks_played == final_counter
    assert len(played(messages)) == 2


def test_echo_and_double_tap_generate_two_copies_without_recursive_replay(monkeypatch):
    helper, player, enemy, combat, messages = prepare(monkeypatch)
    player.add_power(EchoFormPower(amount=1, owner=player))
    player.add_power(DoubleTapPower(amount=1, owner=player))
    card = Strike()
    assert play(helper, card) is None
    assert len(played(messages)) == 3
    assert len(set(map(id, played(messages)))) == 3
    assert combat.combat_state.turn_cards_played == 3
    assert enemy.hp == 982
    assert player.energy == 2
    assert battle_cards(player) == [card]


@pytest.mark.parametrize("power_type", [EchoFormPower, DoubleTapPower, BurstPower])
def test_two_charges_copy_next_two_original_cards_not_the_copies(power_type, monkeypatch):
    helper, player, _, combat, messages = prepare(monkeypatch, energy=5)
    player.add_power(power_type(amount=2, owner=player))
    card_type = Defend if power_type is BurstPower else Strike
    originals = [card_type() for _ in range(3)]
    for card in originals:
        assert play(helper, card) is None
    assert len(played(messages)) == 5
    assert combat.combat_state.turn_cards_played == 5
    assert player.energy == 2
    assert set(map(id, battle_cards(player))) == set(map(id, originals))


@pytest.mark.parametrize("entry", ["chaos", "mayhem", "havoc"])
def test_autoplay_does_not_need_free_hand_slot(entry, monkeypatch):
    helper, player, enemy, _, messages = prepare(monkeypatch)
    full_hand = [Defend() for _ in range(10)]
    player.card_manager.piles["hand"] = full_hand.copy()
    card = Strike()
    helper.add_card_to_draw_pile(card)
    if entry == "chaos":
        assert potion(helper, DistilledChaos()) is None
    elif entry == "mayhem":
        power = MayhemPower(owner=player)
        player.add_power(power)
        power.on_turn_start()
        assert helper.game_state.drive_actions() is None
    else:
        # Havoc itself takes one of the ten hand slots while it is played.
        player.card_manager.piles["hand"].pop()
        assert play(helper, Havoc()) is None
        full_hand.pop()
    assert enemy.hp == 994
    assert card in played(messages)
    assert player.card_manager.piles["hand"] == full_hand
    assert player.card_manager.get_card_location(card) == ("exhaust_pile" if entry == "havoc" else "discard_pile")


def test_chaos_shuffles_initial_discard_before_taking_three_cards(monkeypatch):
    helper, player, _, combat, messages = prepare(monkeypatch)
    cards = [Defend() for _ in range(3)]
    player.card_manager.piles["discard_pile"] = cards.copy()
    assert potion(helper, DistilledChaos()) is None
    assert player.block == 15
    assert combat.combat_state.turn_cards_played == 3
    assert set(map(id, played(messages))) == set(map(id, cards))
    assert set(map(id, player.card_manager.piles["discard_pile"])) == set(map(id, cards))


def test_empty_chaos_and_mayhem_do_not_fabricate_plays(monkeypatch):
    helper, player, _, combat, messages = prepare(monkeypatch)
    assert potion(helper, DistilledChaos()) is None
    power = MayhemPower(owner=player)
    player.add_power(power)
    power.on_turn_start()
    assert helper.game_state.drive_actions() is None
    assert not played(messages)
    assert combat.combat_state.turn_cards_played == 0
    assert not battle_cards(player)


def test_sacred_bark_chaos_plays_six_and_preserves_all_originals(monkeypatch):
    helper, player, _, combat, messages = prepare(monkeypatch, energy=0)
    player.relics.append(SacredBark())
    cards = [Defend() for _ in range(6)]
    player.card_manager.piles["draw_pile"] = cards.copy()
    assert potion(helper, DistilledChaos()) is None
    assert player.block == 30
    assert combat.combat_state.turn_cards_played == 6
    assert len(played(messages)) == 6
    assert set(map(id, battle_cards(player))) == set(map(id, cards))


@pytest.mark.parametrize("energy,cost,expected_plays", [(3, 2, 2), (3, 1, 1), (0, 2, 2)])
def test_necronomicon_cost_threshold_and_autoplay_energy_exemption(energy, cost, expected_plays, monkeypatch):
    helper, player, _, _, messages = prepare(monkeypatch, energy=energy)
    player.relics.append(Necronomicon())
    card = Bash()
    card.cost_until_end_of_turn = cost
    if energy:
        assert play(helper, card) is None
    else:
        helper.add_card_to_draw_pile(card)
        power = MayhemPower(owner=player)
        player.add_power(power)
        power.on_turn_start()
        assert helper.game_state.drive_actions() is None
    assert len(played(messages)) == expected_plays
    assert player.energy == max(0, energy - cost)
    assert battle_cards(player) == [card]


def test_necronomicon_does_not_consume_trigger_on_zero_until_played_bash(monkeypatch):
    helper, player, _, _, messages = prepare(monkeypatch)
    necro = Necronomicon()
    player.relics.append(necro)
    discounted = Bash()
    discounted.cost_until_played = 0
    assert play(helper, discounted) is None
    assert played(messages) == [discounted]
    assert player.energy == 3
    assert not necro.double_attack_played
    assert discounted.cost_until_played is None
    full_cost = Bash()
    assert play(helper, full_cost) is None
    assert len(played(messages)) == 3
    assert player.energy == 1
    assert necro.double_attack_played


def test_omniscience_two_plays_resolve_in_order_and_use_one_original(monkeypatch):
    helper, player, enemy, combat, messages = prepare(monkeypatch, energy=4)
    # CARD-010's hand-vs-draw selection is outside this scheduler regression.
    card = Strike()
    helper.add_card_to_hand(card)
    assert play(helper, Omniscience()) is None
    snapshots = [(m.card, hp) for m, hp, _ in messages if isinstance(m, CardPlayedMessage)]
    assert len(snapshots) == 3
    assert snapshots[1][0] is card
    assert snapshots[2][0] is not card
    assert [hp for _, hp in snapshots] == [1000, 1000, 994]
    assert enemy.hp == 988
    assert player.energy == 0
    assert combat.combat_state.turn_cards_played == 3
    assert player.card_manager.get_card_location(card) == "exhaust_pile"
    assert len(battle_cards(player)) == 2


@pytest.mark.parametrize("card_type", [Strike, Wound])
def test_havoc_exhausts_exactly_once_including_cancelled_card(card_type, monkeypatch):
    helper, player, _, combat, messages = prepare(monkeypatch)
    card = card_type()
    helper.add_card_to_draw_pile(card)
    assert play(helper, Havoc()) is None
    exhausts = [message.card for message, _, _ in messages if isinstance(message, CardExhaustedMessage)]
    assert exhausts == [card]
    assert player.card_manager.get_card_location(card) == "exhaust_pile"
    assert combat.combat_state.turn_cards_played == (2 if card_type is Strike else 1)


def test_replay_of_exhausting_card_purges_copy_without_second_exhaust_event(monkeypatch):
    helper, player, enemy, _, messages = prepare(monkeypatch)
    player.add_power(EchoFormPower(amount=1, owner=player))
    card = Pummel()
    assert play(helper, card) is None
    assert len(played(messages)) == 2
    assert enemy.hp == 984
    assert player.energy == 2
    exhausts = [message.card for message, _, _ in messages if isinstance(message, CardExhaustedMessage)]
    assert exhausts == [card]
    assert player.card_manager.piles["exhaust_pile"] == [card]
    assert battle_cards(player) == [card]


def test_mayhem_last_grand_finale_is_legal_after_removing_it_from_draw(monkeypatch):
    helper, player, enemy, _, messages = prepare(monkeypatch, energy=0)
    card = GrandFinale()
    helper.add_card_to_draw_pile(card)
    power = MayhemPower(owner=player)
    player.add_power(power)
    power.on_turn_start()
    assert helper.game_state.drive_actions() is None
    assert enemy.hp == 950
    assert played(messages) == [card]
    assert player.card_manager.get_card_location(card) == "discard_pile"


@pytest.mark.parametrize("power_type", [EchoFormPower, DoubleTapPower])
def test_replay_of_killing_single_target_attack_does_not_retarget_survivor(power_type, monkeypatch):
    helper, player, enemy, combat, messages = prepare(monkeypatch)
    enemy.hp = 6
    survivor = Cultist()
    survivor._max_hp = 100
    survivor.hp = 100
    combat.enemies.append(survivor)
    player.add_power(power_type(amount=1, owner=player))
    card = Strike()
    assert play(helper, card) is None
    assert enemy.hp == 0
    assert survivor.hp == 100
    assert played(messages) == [card]
    assert combat.combat_state.turn_cards_played == 1
    assert battle_cards(player) == [card]
    assert not player.card_manager.piles.get("limbo")


def test_upgraded_bash_replay_preserves_magic_without_sharing_mutable_values(monkeypatch):
    helper, player, enemy, _, messages = prepare(monkeypatch)
    player.add_power(EchoFormPower(amount=1, owner=player))
    card = Bash()
    card.upgrade()
    assert play(helper, card) is None
    original, replay = played(messages)
    assert original is card and replay is not card
    assert enemy.hp == 975  # 10, then 15 after the first Bash's Vulnerable.
    vulnerable = enemy.get_power("Vulnerable")
    assert vulnerable is not None and vulnerable.amount == 6
    assert replay.get_magic_value("vulnerable") == 3
    # The disposable instance must not carry a mutable alias back to the real card.
    replay._magic["vulnerable"] = 99
    assert card.get_magic_value("vulnerable") == 3


@pytest.mark.parametrize("power_type", [EchoFormPower, BurstPower])
def test_replayed_entrench_reads_block_after_first_effect_resolves(power_type, monkeypatch):
    helper, player, _, combat, messages = prepare(monkeypatch)
    player.block = 5
    player.add_power(power_type(amount=1, owner=player))
    card = Entrench()
    assert play(helper, card) is None
    assert player.block == 20
    assert player.energy == 1
    assert combat.combat_state.turn_cards_played == 2
    snapshots = [block for message, _, block in messages if isinstance(message, CardPlayedMessage)]
    assert snapshots == [5, 10]
