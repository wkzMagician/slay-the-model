"""R-06: relic counters, dynamic descriptions, and shared presentation."""
from types import SimpleNamespace
from typing import cast

import pytest

import localization
from actions.display import DisplayTextAction
from ai.context_builder import AIContextBuilder
from cards.colorless.injury import Injury
from cards.ironclad.strike import Strike
from enemies.act1.cultist import Cultist
from engine.messages import CombatEndedMessage
from map.map_manager import MapManager
from relics.base import Relic
from relics.character.defect import Inserter
from relics.global_relics.boss import VelvetChoker
from relics.global_relics.common import (
    AncientTeaSet, HappyFlower, MawBank, Nunchaku, Omamori, PenNib, TinyChest,
)
from relics.global_relics.rare import (
    CaptainsWheel, DuVuDoll, Girya, LizardTail, Pocketwatch, StoneCalendar,
)
from relics.global_relics.special import NeowsLament
from relics.global_relics.uncommon import (
    HornCleat, InkBottle, Kunai, LetterOpener, Matryoshka, OrnamentalFan,
    Shuriken, Sundial,
)
from tests.test_combat_utils import create_test_helper
from tui.app import DisplayPanel
from tui.handlers.display_handler import DisplayHandler
from utils.registry import get_registered
from utils.types import RoomType


@pytest.fixture(autouse=True)
def fresh_state():
    language = localization.current_language
    create_test_helper()
    localization.set_language('en')
    yield
    localization.set_language(language)


@pytest.mark.parametrize('cls,field,target', [
    (HappyFlower, 'turn_counter', 3), (Nunchaku, 'attacks_played', 10),
    (PenNib, 'attacks_played', 10), (InkBottle, 'cards_played', 10),
    (Sundial, 'shuffle_count', 3), (TinyChest, 'event_count', 4),
])
def test_run_counters_read_live_fields_and_show_zero(cls, field, target):
    relic = cls()
    assert relic.counter_value() == 0
    assert relic.status_text() == f'0/{target}'
    setattr(relic, field, target - 1)
    assert relic.status_text() == f'{target - 1}/{target}'
    assert relic.display_name() in relic.info()


@pytest.mark.parametrize('cls,field,initial', [
    (NeowsLament, 'stacks', 3), (Omamori, 'curses_to_negate', 2),
    (Matryoshka, 'chests_to_spawn', 2),
])
@pytest.mark.parametrize('lang', ['en', 'zh'])
def test_remaining_uses_and_exhausted_descriptions(cls, field, initial, lang):
    localization.set_language(lang)
    relic = cls()
    assert str(initial) in relic.status_text()
    setattr(relic, field, 1)
    assert '1' in relic.display_description()
    setattr(relic, field, 0)
    assert relic.description_key() == 'description_exhausted'
    assert localization.t('ui.relic_status.exhausted') in relic.display_name()
    assert 'relics.' not in relic.info()
    assert '{remaining}' not in relic.info()


@pytest.mark.parametrize('cls,field,target', [
    (Kunai, 'attacks_played_this_turn', 3),
    (Shuriken, 'attacks_played_this_turn', 3),
    (OrnamentalFan, 'attacks_played_this_turn', 3),
    (LetterOpener, 'skills_played_this_turn', 3),
    (Pocketwatch, 'cards_played_this_turn', None),
    (VelvetChoker, None, 6),
])
def test_turn_counters_hide_between_turns_and_after_combat(cls, field, target):
    helper = create_test_helper()
    relic = cls()
    player = helper.create_player()
    player.relics = [relic]
    assert relic.counter_value() is None
    combat = helper.start_combat([helper.create_enemy(Cultist, hp=100)])
    helper.game_state.drive_actions()
    if field:
        setattr(relic, field, 2)
    else:
        combat.combat_state.turn_cards_played = 2
    assert relic.counter_value() == 2
    assert relic.counter_target() == target
    combat.combat_state.current_phase = 'enemy_action'
    assert relic.status_text() == ''
    combat.combat_state.current_phase = 'player_action'
    helper.game_state.publish_message(CombatEndedMessage(owner=player, enemies=[]))
    helper.game_state.drive_actions()
    assert relic.counter_value() is None
    helper.start_combat([helper.create_enemy(Cultist, hp=100)])
    helper.game_state.drive_actions()
    assert relic.counter_value() is not None


@pytest.mark.parametrize('cls,turn', [(HornCleat, 2), (CaptainsWheel, 3), (StoneCalendar, 7)])
def test_one_shot_counters_hide_on_actual_trigger_and_reset_next_combat(cls, turn):
    helper = create_test_helper()
    relic = cls()
    player = helper.create_player()
    player.relics = [relic]
    enemy = helper.create_enemy(Cultist, hp=1000)
    combat = helper.start_combat([enemy])
    helper.game_state.drive_actions()
    combat.combat_state.combat_turn = 1
    assert relic.counter_value() == 1
    combat.combat_state.combat_turn = turn
    if cls is StoneCalendar:
        relic.on_player_turn_end()
    else:
        relic.on_player_turn_start()
    helper.game_state.drive_actions()
    assert relic.counter_value() is None
    helper.start_combat([enemy], floor=2)
    helper.game_state.drive_actions()
    assert relic.counter_value() == 0


def test_girya_displays_used_count_and_inserter_displays_cycle_without_changing_rules():
    relic = Girya()
    for remaining in range(4):
        relic.uses_remaining = remaining
        assert relic.counter_value() == 3 - remaining
        assert f'{3 - remaining}/3' in relic.status_text()
    inserter = Inserter()
    inserter.counter = 5
    assert inserter.status_text() == '1/2'
    assert inserter.counter == 5


def test_duvu_counts_permanent_curses_not_combat_piles():
    helper = create_test_helper()
    player = helper.game_state.player
    doll = DuVuDoll()
    player.card_manager.piles['deck'] = [Injury(), Injury(), Strike()]
    player.card_manager.piles['hand'] = [Injury()]
    assert doll.counter_value() == 2
    assert '2' in doll.display_description()
    player.card_manager.piles['deck'].pop(0)
    assert doll.counter_value() == 1
    assert '1' in doll.display_description()


@pytest.mark.parametrize('lang', ['en', 'zh'])
def test_neow_has_one_definition_and_three_uses_with_localized_messages(lang):
    from relics.global_relics.event import NeowsLament as LegacyNeow
    from relics import NeowsLament as ExportedNeow

    assert LegacyNeow is ExportedNeow is NeowsLament
    assert get_registered('relic', 'NeowsLament') is NeowsLament
    localization.set_language(lang)
    helper = create_test_helper()
    player = helper.game_state.player
    relic = NeowsLament()
    player.relics = [relic]
    for index in range(4):
        enemy = helper.create_enemy(Cultist, hp=50)
        helper.start_combat([enemy], floor=index + 1)
        messages = [action for action in helper.game_state.action_queue.queue if isinstance(action, DisplayTextAction)]
        assert len(messages) == (1 if index < 3 else 0)
        if messages:
            message = cast(DisplayTextAction, messages[0])
            text = localization.t(message.text_key, **message.fmt)
            assert str(2 - index) in text
            assert 'relics.' not in text
        helper.game_state.drive_actions()
        assert enemy.hp == (1 if index < 3 else 50)
        assert enemy.max_hp == 50
    assert relic.stacks == 0
    assert relic.description_key() == 'description_exhausted'


def test_tiny_chest_counts_since_pickup_and_survives_act_change():
    helper = create_test_helper()
    manager = MapManager(seed=42)
    for _ in range(3):
        manager._resolve_unknown_type(5)
    relic = TinyChest()
    helper.game_state.player.relics = [relic]
    for expected in (1, 2, 3):
        manager._resolve_unknown_type(5)
        assert relic.event_count == expected
    manager = MapManager(seed=42, act_id=2)
    assert manager._resolve_unknown_type(5) == RoomType.TREASURE
    assert relic.event_count == 0
    assert manager.unknown_room_visits[RoomType.TREASURE] == 0
    assert relic.status_text() == '0/4'


def test_non_numeric_markers_never_expose_sentinels():
    tail = LizardTail()
    tail.can_revive = False
    bank = MawBank()
    bank.still_working = False
    tea = AncientTeaSet()
    tea.is_rest_last_room = True
    assert tail.status_text() == bank.status_text() == 'Exhausted'
    assert tea.status_text() == 'Ready'
    assert Relic().status_text() == ''


@pytest.mark.parametrize('lang', ['en', 'zh'])
def test_all_display_entry_points_use_same_name_and_description(lang, monkeypatch):
    localization.set_language(lang)
    helper = create_test_helper()
    player = helper.game_state.player
    relic = Omamori()
    relic.curses_to_negate = 1
    player.relics = [relic]
    combat = helper.start_combat([helper.create_enemy(Cultist, hp=100)])
    helper.game_state.drive_actions()
    app = SimpleNamespace(update_player_info=lambda *args: None, update_display_content=lambda text: output.append(text))
    output = []
    DisplayHandler(app).display_combat(combat, helper.game_state)
    assert relic.display_name() in output[-1]
    # Detail rendering uses the same dynamic description as info().
    assert relic.display_description() in output[-1]
    panel = DisplayPanel()
    monkeypatch.setattr(panel, '_refresh_display', lambda: None)
    panel.update_player_info(player, helper.game_state)
    assert relic.display_name() in panel.player_info
    assert relic.display_name() in relic.info()
    assert relic.display_description() in relic.info()
    context = AIContextBuilder._build_relics_info(helper.game_state)
    assert relic.display_name() in context
    assert relic.display_description() in context
    assert "{remaining}" not in context
