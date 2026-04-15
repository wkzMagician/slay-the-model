import pytest

from actions.card import AddCardAction, DiscardCardAction, DrawCardsAction, ShuffleAction
from actions.combat import PlayCardBHAction
from cards.colorless.dazed import Dazed
from cards.colorless.doubt import Doubt
from cards.colorless.void import Void
from cards.ironclad.pommel_strike import PommelStrike
from cards.ironclad.shrug_it_off import ShrugItOff
from cards.ironclad.strike import Strike
from cards.watcher.deus_ex_machina import DeusExMachina
from enemies.act1.cultist import Cultist
from powers.definitions.rage import RagePower
from relics.global_relics.boss import RunicPyramid
from relics.global_relics.common import CeramicFish
from relics.character.silent import ToughBandages
from relics.global_relics.uncommon import DarkstonePeriapt, Sundial
from tests.test_combat_utils import create_test_helper


def test_card_actions_import_from_actions_card_surface():
    from actions import card as card_surface
    from actions.card_choice import ChooseMoveCardAction
    from actions.card_lifecycle import DrawCardsAction as LifecycleDrawCardsAction
    from actions.card_lifecycle import ExhaustCardAction as LifecycleExhaustCardAction

    assert card_surface.DrawCardsAction is LifecycleDrawCardsAction
    assert card_surface.ExhaustCardAction is LifecycleExhaustCardAction
    assert card_surface.ChooseMoveCardAction is ChooseMoveCardAction


def _capture_published_message_types(game_state, monkeypatch):
    original_publish = game_state.publish_message
    published = []

    def wrapped(message, *args, **kwargs):
        published.append(type(message).__name__)
        return original_publish(message, *args, **kwargs)

    monkeypatch.setattr(game_state, "publish_message", wrapped)
    return published


def test_play_card_action_publishes_card_played_message(monkeypatch):
    helper = create_test_helper()
    player = helper.create_player(hp=80, max_hp=80, energy=3)
    enemy = helper.create_enemy(Cultist, hp=20)
    helper.start_combat([enemy])

    attack = Strike()
    helper.add_card_to_hand(attack)
    player.add_power(RagePower(amount=3, owner=player))

    published = _capture_published_message_types(helper.game_state, monkeypatch)

    PlayCardBHAction(card=attack, targets=[enemy]).execute()
    helper.game_state.drive_actions()

    assert "CardPlayedMessage" in published
    assert player.block == 3


def test_discard_card_action_publishes_card_discarded_message(monkeypatch):
    helper = create_test_helper()
    player = helper.create_player(hp=80, max_hp=80, energy=3)
    enemy = helper.create_enemy(Cultist, hp=20)
    helper.start_combat([enemy])

    discard_target = Strike()
    helper.add_card_to_hand(discard_target)
    player.relics.append(ToughBandages())

    published = _capture_published_message_types(helper.game_state, monkeypatch)

    DiscardCardAction(card=discard_target, source_pile="hand").execute()
    helper.game_state.drive_actions()

    assert "CardDiscardedMessage" in published
    assert discard_target in player.card_manager.get_pile("discard_pile")
    assert player.block == 3


def test_draw_cards_action_publishes_card_drawn_message(monkeypatch):
    helper = create_test_helper()
    player = helper.create_player(hp=80, max_hp=80, energy=3)
    enemy = helper.create_enemy(Cultist, hp=20)
    helper.start_combat([enemy])

    status_card = Void()
    helper.add_card_to_draw_pile(status_card)
    published = _capture_published_message_types(helper.game_state, monkeypatch)

    DrawCardsAction(count=1).execute()
    helper.game_state.drive_actions()

    assert "CardDrawnMessage" in published
    assert status_card in player.card_manager.get_pile("hand")
    assert player.energy == 2


def test_deus_ex_machina_on_draw_adds_miracles_and_exhausts_self():
    helper = create_test_helper()
    player = helper.create_player(hp=80, max_hp=80, energy=3)
    enemy = helper.create_enemy(Cultist, hp=20)
    helper.start_combat([enemy])

    player.card_manager.get_pile("draw_pile").clear()
    player.card_manager.get_pile("hand").clear()
    player.card_manager.get_pile("exhaust_pile").clear()

    deus = DeusExMachina()
    helper.add_card_to_draw_pile(deus)

    DrawCardsAction(count=1).execute()
    helper.game_state.drive_actions()

    hand = player.card_manager.get_pile("hand")
    miracles_in_hand = [card for card in hand if card.__class__.__name__ == "Miracle"]
    assert len(miracles_in_hand) == deus.get_magic_value("count")
    assert deus not in hand
    assert deus in player.card_manager.get_pile("exhaust_pile")


def test_auto_shuffle_from_empty_draw_publishes_shuffle_message(monkeypatch):
    """Empty-deck reshuffle (discard → draw) must emit ShuffleMessage like ShuffleAction."""
    helper = create_test_helper()
    player = helper.create_player(hp=80, max_hp=80, energy=3)
    enemy = helper.create_enemy(Cultist, hp=20)
    helper.start_combat([enemy])

    player.card_manager.piles["draw_pile"].clear()
    helper.add_card_to_discard_pile(Void())

    published = _capture_published_message_types(helper.game_state, monkeypatch)

    DrawCardsAction(count=1).execute()
    helper.game_state.drive_actions()

    assert published.count("ShuffleMessage") == 1
    assert "CardDrawnMessage" in published


def test_draw_many_stops_after_one_shuffle_when_not_enough_cards(monkeypatch):
    """抽牌数大于抽牌堆+弃牌堆可提供的张数时：洗入弃牌只触发一次计数，之后弃牌空则不再抽。"""
    helper = create_test_helper()
    player = helper.create_player(hp=80, max_hp=80, energy=3)
    enemy = helper.create_enemy(Cultist, hp=20)
    helper.start_combat([enemy])

    player.card_manager.piles["draw_pile"].clear()
    for _ in range(3):
        helper.add_card_to_discard_pile(Void())

    published = _capture_published_message_types(helper.game_state, monkeypatch)

    DrawCardsAction(count=5).execute()
    helper.game_state.drive_actions()

    assert published.count("ShuffleMessage") == 2
    assert published.count("CardDrawnMessage") == 3


def test_auto_shuffle_skips_message_when_discard_empty(monkeypatch):
    helper = create_test_helper()
    player = helper.create_player(hp=80, max_hp=80, energy=3)
    enemy = helper.create_enemy(Cultist, hp=20)
    helper.start_combat([enemy])

    player.card_manager.piles["draw_pile"].clear()
    player.card_manager.piles["discard_pile"].clear()

    published = _capture_published_message_types(helper.game_state, monkeypatch)

    DrawCardsAction(count=1).execute()
    helper.game_state.drive_actions()

    assert published.count("ShuffleMessage") == 1


def test_sundial_with_pommel_plus_and_shrug_it_off_shuffle_count_and_energy(monkeypatch):
    """抽/弃皆空、手牌剑柄+与耸肩：先剑柄再耸肩洗牌计数 2 不回能；重置后先耸肩再剑柄计数 3 并回 2 能。

    依赖当前 shuffle_discard_to_draw 在弃牌为空时仍会发布 ShuffleMessage 的行为。
    """
    helper = create_test_helper()
    player = helper.create_player(hp=80, max_hp=80, energy=3)
    enemy = helper.create_enemy(Cultist, hp=50)
    helper.start_combat([enemy])

    sundial = Sundial()
    player.relics.append(sundial)
    assert sundial.shuffle_count == 0

    player.card_manager.piles["draw_pile"].clear()
    player.card_manager.piles["discard_pile"].clear()

    pommel = PommelStrike()
    pommel.upgrade()
    shrug = ShrugItOff()
    helper.add_card_to_hand(pommel)
    helper.add_card_to_hand(shrug)

    published = _capture_published_message_types(helper.game_state, monkeypatch)

    helper.play_card(pommel, target=enemy)
    helper.game_state.drive_actions()
    helper.play_card(shrug, target=player)
    helper.game_state.drive_actions()

    assert published.count("ShuffleMessage") == 2
    assert sundial.shuffle_count == 2
    assert player.energy == 1

    published.clear()

    sundial.shuffle_count = 0
    player.card_manager.piles["hand"].clear()
    player.card_manager.piles["draw_pile"].clear()
    player.card_manager.piles["discard_pile"].clear()
    player.energy = 3

    pommel2 = PommelStrike()
    pommel2.upgrade()
    shrug2 = ShrugItOff()
    helper.add_card_to_hand(shrug2)
    helper.add_card_to_hand(pommel2)

    helper.play_card(shrug2, target=player)
    helper.game_state.drive_actions()
    helper.play_card(pommel2, target=enemy)
    helper.game_state.drive_actions()

    assert published.count("ShuffleMessage") == 3
    assert sundial.shuffle_count == 0
    assert player.energy == 3


def test_shuffle_action_publishes_shuffle_message(monkeypatch):
    helper = create_test_helper()
    player = helper.create_player(hp=80, max_hp=80, energy=1, max_energy=3)
    enemy = helper.create_enemy(Cultist, hp=20)
    helper.start_combat([enemy])

    helper.add_card_to_hand(Strike())
    helper.add_card_to_discard_pile(Strike())
    sundial = Sundial()
    sundial.shuffle_count = 2
    player.relics.append(sundial)

    published = _capture_published_message_types(helper.game_state, monkeypatch)

    ShuffleAction().execute()
    helper.game_state.drive_actions()

    assert "ShuffleMessage" in published
    assert player.energy == 3


def test_add_card_action_publishes_card_added_message(monkeypatch):
    helper = create_test_helper()
    player = helper.create_player(hp=80, max_hp=80, energy=3)
    curse_card = Doubt()
    player.relics.extend([CeramicFish(), DarkstonePeriapt()])
    initial_gold = player.gold
    initial_max_hp = player.max_hp

    published = _capture_published_message_types(helper.game_state, monkeypatch)

    AddCardAction(card=curse_card, dest_pile="deck", source="reward").execute()
    helper.game_state.drive_actions()

    assert "CardAddedToPileMessage" in published
    assert curse_card in player.card_manager.get_pile("deck")
    assert player.gold == initial_gold + 9
    assert player.max_hp == initial_max_hp + 6


def test_end_turn_discard_does_not_publish_message_or_trigger_discard_effects(monkeypatch):
    helper = create_test_helper()
    player = helper.create_player(hp=80, max_hp=80, energy=3)
    enemy = helper.create_enemy(Cultist, hp=20)
    combat = helper.start_combat([enemy])

    discard_target = Strike()
    helper.add_card_to_hand(discard_target)
    player.relics.append(ToughBandages())

    published = _capture_published_message_types(helper.game_state, monkeypatch)

    combat._end_player_phase()
    helper.game_state.drive_actions()

    assert "CardDiscardedMessage" not in published
    assert discard_target in player.card_manager.get_pile("discard_pile")
    assert player.block == 0


def test_end_turn_ethereal_dazed_goes_to_exhaust_pile():
    helper = create_test_helper()
    player = helper.create_player(hp=80, max_hp=80, energy=3)
    enemy = helper.create_enemy(Cultist, hp=20)
    combat = helper.start_combat([enemy])

    dazed = Dazed()
    helper.add_card_to_hand(dazed)

    combat._end_player_phase()
    helper.game_state.drive_actions()

    assert dazed not in player.card_manager.get_pile("hand")
    assert dazed in player.card_manager.get_pile("exhaust_pile")
    assert dazed not in player.card_manager.get_pile("discard_pile")


def test_end_turn_ethereal_dazed_exhausts_with_runic_pyramid_non_ethereal_stays_in_hand():
    helper = create_test_helper()
    player = helper.create_player(hp=80, max_hp=80, energy=3)
    enemy = helper.create_enemy(Cultist, hp=20)
    combat = helper.start_combat([enemy])

    player.relics.append(RunicPyramid())
    dazed = Dazed()
    strike = Strike()
    helper.add_card_to_hand(dazed)
    helper.add_card_to_hand(strike)

    combat._end_player_phase()
    helper.game_state.drive_actions()

    assert dazed not in player.card_manager.get_pile("hand")
    assert dazed in player.card_manager.get_pile("exhaust_pile")
    assert strike in player.card_manager.get_pile("hand")
    assert strike not in player.card_manager.get_pile("discard_pile")
