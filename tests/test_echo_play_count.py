"""Echo Form uses all original plays this turn, including before it was gained."""

from actions.combat_cards import PlayCardAction
from cards.defect.beam_cell import BeamCell
from cards.defect.echo_form import EchoForm
from cards.ironclad.strike import Strike
from enemies.act1.cultist import Cultist
from engine.messages import CardPlayedMessage
from powers.definitions.echo_form import EchoFormPower
from tests.test_combat_utils import create_test_helper


def prepare(monkeypatch):
    helper = create_test_helper()
    player = helper.create_player(hp=100, max_hp=100, energy=10)
    player.base_draw_count = 0
    enemy = Cultist()
    enemy._max_hp = 1000
    enemy.hp = 1000
    combat = helper.start_combat([enemy])
    assert helper.game_state.drive_actions() is None
    played = []
    original = helper.game_state.publish_message

    def publish(message, *args, **kwargs):
        if isinstance(message, CardPlayedMessage):
            played.append(message.card)
        return original(message, *args, **kwargs)

    monkeypatch.setattr(helper.game_state, "publish_message", publish)
    return helper, player, enemy, combat, played


def play(helper, card):
    helper.add_card_to_hand(card)
    helper.game_state.add_action(PlayCardAction(card))
    assert helper.game_state.drive_actions() is None


def test_echo_gained_by_playing_echo_form_does_not_copy_second_card(monkeypatch):
    helper, player, enemy, combat, played = prepare(monkeypatch)
    echo, beam = EchoForm(), BeamCell()
    play(helper, echo)
    play(helper, beam)
    assert played == [echo, beam]
    assert enemy.hp == 997
    assert combat.combat_state.turn_cards_played == 2
    power = player.get_power("Echo Form")
    assert power is not None and power.cards_doubled_this_turn == 0


def test_real_next_turn_resets_echo_eligibility_and_recalculates_beam(monkeypatch):
    helper, _, enemy, combat, played = prepare(monkeypatch)
    play(helper, EchoForm())
    combat._start_player_turn()
    assert helper.game_state.drive_actions() is None
    played.clear()
    beam = BeamCell()
    play(helper, beam)
    assert len(played) == 2
    assert played[0] is beam and played[1] is not beam
    assert enemy.hp == 993  # First Beam applies Vulnerable before its replay.
    assert combat.combat_state.turn_cards_played == 2


def test_two_echo_stacks_count_originals_without_counting_their_replays(monkeypatch):
    helper, player, enemy, combat, played = prepare(monkeypatch)
    power = EchoFormPower(amount=2, owner=player)
    player.add_power(power)
    originals = [Strike() for _ in range(3)]
    for card in originals:
        play(helper, card)
    assert len(played) == 5
    assert [card for card in played if not getattr(card, "_is_replay", False)] == originals
    assert enemy.hp == 970
    assert power.cards_doubled_this_turn == 2
    assert combat.combat_state.turn_cards_played == 5


def test_midturn_echo_stacking_uses_existing_original_play_count(monkeypatch):
    helper, player, enemy, _, played = prepare(monkeypatch)
    # Prepared power application after an actual first play isolates stacking.
    play(helper, Strike())
    power = EchoFormPower(amount=1, owner=player)
    player.add_power(power)
    player.add_power(EchoFormPower(amount=1, owner=player))
    play(helper, Strike())
    play(helper, Strike())
    assert len(played) == 4
    assert enemy.hp == 976
    assert power.amount == 2 and power.cards_doubled_this_turn == 1


def test_next_turn_clears_prior_echo_copy_counter(monkeypatch):
    helper, player, enemy, combat, played = prepare(monkeypatch)
    power = EchoFormPower(amount=1, owner=player)
    player.add_power(power)
    play(helper, Strike())
    assert power.cards_doubled_this_turn == 1
    combat._start_player_turn()
    assert helper.game_state.drive_actions() is None
    assert power.cards_doubled_this_turn == 0
    played.clear()
    play(helper, Strike())
    play(helper, Strike())
    assert len(played) == 3
    assert enemy.hp == 970
    assert power.cards_doubled_this_turn == 1
