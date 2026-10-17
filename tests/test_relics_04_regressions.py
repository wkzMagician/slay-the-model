"""Regression coverage for .bugs/04-relics R-01 through R-05."""
import pytest

from actions.combat_cards import PlayCardBHAction
from cards.ironclad.defend import Defend
from cards.ironclad.strike import Strike
from cards.ironclad.twin_strike import TwinStrike
from cards.ironclad.cleave import Cleave
from cards.watcher.wreath_of_flame import WreathOfFlame
from enemies.act1.cultist import Cultist
from powers.definitions.vigor import VigorPower
from relics.global_relics.common import Akabeko, HappyFlower, PenNib
from relics.global_relics.uncommon import (
    Kunai, Shuriken, OrnamentalFan, LetterOpener, Pantograph,
)
from tests.test_combat_utils import create_test_helper
from utils.types import EnemyType


def setup_combat(relics=(), hp=80, enemy_types=(EnemyType.NORMAL,)):
    helper = create_test_helper()
    player = helper.create_player(hp=hp, max_hp=80, energy=100)
    player.relics = list(relics)
    enemies = [helper.create_enemy(Cultist, hp=1000) for _ in enemy_types]
    for enemy, enemy_type in zip(enemies, enemy_types):
        enemy.enemy_type = enemy_type
    combat = helper.start_combat(enemies)
    helper.game_state.drive_actions()
    return helper, player, enemies, combat


def play(helper, card, targets):
    PlayCardBHAction(card, targets).execute()
    helper.game_state.drive_actions()


def test_flower_grants_energy_at_turn_start_and_preserves_progress():
    relic = HappyFlower()
    helper, player, enemies, combat = setup_combat([relic])
    for _ in range(2):
        # First two turns: neither should trigger.
        combat._start_player_turn()
        helper.game_state.drive_actions()
        assert player.energy == 100
    relic.on_player_turn_end()
    assert relic.turn_counter == 2
    combat = helper.start_combat(enemies, floor=2)
    helper.game_state.drive_actions()
    combat._start_player_turn()
    helper.game_state.drive_actions()
    assert player.energy == 101
    assert relic.turn_counter == 0


def test_pen_nib_restores_primed_power_across_combats_and_resets_after_tenth():
    relic = PenNib()
    helper, player, enemies, _ = setup_combat([relic])
    for _ in range(9):
        play(helper, Strike(), enemies)
    assert relic.attacks_played == 9
    assert player.get_power('PenNib') is not None
    helper.start_combat(enemies, floor=2)
    helper.game_state.drive_actions()
    assert relic.attacks_played == 9
    assert player.get_power('PenNib') is not None
    hp = enemies[0].hp
    play(helper, TwinStrike(), enemies)
    assert enemies[0].hp == hp - 20
    assert relic.attacks_played == 0
    assert player.get_power('PenNib') is None
    for _ in range(9):
        play(helper, Strike(), enemies)
    hp = enemies[0].hp
    play(helper, Strike(), enemies)
    assert enemies[0].hp == hp - 12
    assert relic.attacks_played == 0


@pytest.mark.parametrize('enemy_types,expected', [
    ((EnemyType.NORMAL,), 30),
    ((EnemyType.ELITE,), 30),
    ((EnemyType.BOSS,), 55),
    ((EnemyType.BOSS, EnemyType.BOSS), 55),
])
def test_pantograph_heals_only_boss_encounters_immediately(enemy_types, expected):
    _, player, _, _ = setup_combat([Pantograph()], hp=30, enemy_types=enemy_types)
    assert player.hp == expected
    assert player.get_power('Regeneration') is None


def test_akabeko_and_wreath_share_vigor_and_buff_all_hits_once():
    helper, player, enemies, _ = setup_combat([Akabeko()])
    vigor_power = player.get_power('Vigor')
    assert vigor_power is not None
    assert vigor_power.amount == 8
    play(helper, WreathOfFlame(), [player])
    vigor = [power for power in player.powers if isinstance(power, VigorPower)]
    assert len(vigor) == 1
    assert vigor[0].amount == 13
    play(helper, Defend(), [player])
    vigor_power = player.get_power('Vigor')
    assert vigor_power is not None
    assert vigor_power.amount == 13
    play(helper, TwinStrike(), enemies)
    assert enemies[0].hp == 1000 - 36
    assert player.get_power('Vigor') is None
    play(helper, TwinStrike(), enemies)
    assert enemies[0].hp == 1000 - 46


def test_vigor_buffs_every_target_then_expires_and_reapplies_next_combat():
    helper, player, enemies, _ = setup_combat(
        [Akabeko()], enemy_types=(EnemyType.NORMAL, EnemyType.NORMAL),
    )
    play(helper, Cleave(), enemies)
    assert [enemy.hp for enemy in enemies] == [984, 984]
    assert player.get_power('Vigor') is None
    helper.start_combat(enemies, floor=2)
    helper.game_state.drive_actions()
    vigor_power = player.get_power('Vigor')
    assert vigor_power is not None
    assert vigor_power.amount == 8


@pytest.mark.parametrize('relic_cls,card_cls,power_name,block,damage', [
    (Kunai, Strike, 'Dexterity', 0, 0),
    (Shuriken, Strike, 'Strength', 0, 0),
    (OrnamentalFan, Strike, None, 12, 0),
    (LetterOpener, Defend, None, 45, 15),
])
def test_three_card_relics_repeat_and_reset_each_turn(relic_cls, card_cls, power_name, block, damage):
    relic = relic_cls()
    helper, player, enemies, combat = setup_combat([relic])
    attr = 'skills_played_this_turn' if relic_cls is LetterOpener else 'attacks_played_this_turn'
    # Wrong card type does not advance the counter.
    other = Strike() if relic_cls is LetterOpener else Defend()
    relic.on_card_play(other, enemies)
    assert getattr(relic, attr) == 0
    for index in range(9):
        play(helper, card_cls(), [player] if relic_cls is LetterOpener else enemies)
        assert getattr(relic, attr) == (index + 1) % 3
    if power_name:
        power = player.get_power(power_name)
        assert power is not None
        assert power.amount == 3
    else:
        assert player.block == block
    if damage:
        assert enemies[0].hp == 1000 - damage
    play(helper, card_cls(), [player] if relic_cls is LetterOpener else enemies)
    assert getattr(relic, attr) == 1
    combat._start_player_turn()
    helper.game_state.drive_actions()
    assert getattr(relic, attr) == 0


def test_vigor_survives_turns_and_combines_with_pen_nib():
    nib = PenNib()
    nib.attacks_played = 9
    helper, player, enemies, combat = setup_combat([Akabeko(), nib])
    combat._start_player_turn()
    helper.game_state.drive_actions()
    combat._start_player_turn()
    helper.game_state.drive_actions()
    vigor_power = player.get_power("Vigor")
    assert vigor_power is not None
    assert vigor_power.amount == 8
    play(helper, TwinStrike(), enemies)
    assert enemies[0].hp == 1000 - 52
    assert player.get_power("Vigor") is None
    assert player.get_power("PenNib") is None
