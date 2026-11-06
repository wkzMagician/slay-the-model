"""Original display ordering and shared console/TUI behavior, without RNG."""
import random
from types import SimpleNamespace

import pytest

from cards.base import Card, RawLocalStr
from engine.combat import Combat
import engine.combat as combat_module
from engine.game_state import game_state
from localization import set_language, t
from relics.global_relics.shop import FrozenEye
from tui.handlers.display_handler import DisplayHandler
from utils.card_display import draw_pile_display_order
from utils.types import CardType, RarityType


def card(name, rarity=RarityType.COMMON, card_type=CardType.SKILL):
    result = Card()
    result.display_name = RawLocalStr(name)
    result.rarity = rarity
    result.card_type = card_type
    return result


def test_original_rarity_name_and_status_priority():
    basic = card("Z basic", RarityType.STARTER)
    special = card("Z special", RarityType.SPECIAL)
    common_b = card("B common")
    common_a = card("A common")
    uncommon = card("A uncommon", RarityType.UNCOMMON)
    rare = card("A rare", RarityType.RARE)
    curse = card("A curse", RarityType.CURSE, CardType.CURSE)
    status = card("A status", RarityType.SPECIAL, CardType.STATUS)
    status_b = card("B status", RarityType.SPECIAL, CardType.STATUS)
    pile = [status_b, rare, common_b, basic, curse, common_a, status, uncommon, special]
    original = list(pile)
    assert draw_pile_display_order(pile) == [basic, special, common_a, common_b, uncommon, rare, curse, status, status_b]
    assert pile == original


def test_equal_keys_keep_original_view_order_and_compare_case_and_upgrade_names():
    first, second = card("Strike"), card("Strike")
    plus, lower = card("Strike+"), card("strike")
    pile = [lower, plus, first, second]
    assert draw_pile_display_order(pile) == [second, first, plus, lower]


def test_name_order_matches_java_utf16_instead_of_python_codepoints():
    astral, bmp = card("\U00010000"), card("\ue000")
    assert draw_pile_display_order([bmp, astral]) == [astral, bmp]


@pytest.mark.parametrize("reveal", [False, True])
def test_empty_singleton_and_frozen_eye_order(reveal):
    assert draw_pile_display_order([], reveal) == []
    only = card("Only")
    assert draw_pile_display_order([only], reveal) == [only]
    pile = [card("A"), card("Z"), card("M")]
    expected = list(reversed(pile)) if reveal else [pile[0], pile[2], pile[1]]
    assert draw_pile_display_order(pile, reveal) == expected


@pytest.mark.parametrize("language", ["en", "zh"])
@pytest.mark.parametrize("reveal", [False, True])
def test_console_and_tui_use_same_view_without_mutating_piles_or_any_rng(monkeypatch, language, reveal):
    game_state.config.language = language
    set_language(language)
    pile = [card("Zulu", RarityType.RARE), card("Beta"), card("Alpha"),
            card("Status", RarityType.SPECIAL, CardType.STATUS)]
    game_state.player.card_manager.piles["draw_pile"] = pile
    game_state.player.relics = [FrozenEye()] if reveal else []
    combat = Combat(enemies=[])
    expected_names = ["Status", "Alpha", "Beta", "Zulu"] if reveal else ["Alpha", "Beta", "Zulu", "Status"]
    expected_line = f"{t('ui.draw_pile', default='Draw Pile')} (4): {', '.join(expected_names)}"
    original_pile = list(pile)
    before = game_state.random_streams.export_state()
    global_before = random.getstate()
    console, tui = [], []
    monkeypatch.setattr(combat_module, "tui_print", lambda text="": console.append(text))
    handler = DisplayHandler(SimpleNamespace(update_display_content=tui.append,
                                             update_player_info=lambda *_: None))
    for _ in range(2):
        combat._print_combat_state()
        handler.display_combat(combat, game_state)
    assert [line.strip() for line in console if expected_line in line] == [expected_line] * 2
    assert all(expected_line in text.splitlines() for text in tui)
    assert pile == original_pile
    assert game_state.random_streams.export_state() == before
    assert random.getstate() == global_before
