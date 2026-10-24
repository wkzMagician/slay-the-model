"""Regressions for the four defects blocking lifecycle continuations."""
import random

import pytest

from actions.combat import LoseMaxHPAction, ModifyMaxHpAction
from actions.combat_cards import PlayCardAction
from actions.reward import AddEliteRelicAction
from cards.ironclad.combust import Combust
from cards.ironclad.strike import Strike
from enemies.act1.acid_slime import AcidSlimeL
from enemies.act1.cultist import Cultist
from enemies.act1.slime_boss import SlimeBoss
from enemies.act1.spike_slime import SpikeSlimeL
from player.player import Player
from relics.base import Relic
from relics.character.ironclad import MagicFlower
from relics.global_relics.boss import BlackStar, BustedCrown
from relics.global_relics.event import MarkOfBloom
from relics.global_relics.rare import PrayerWheel
from relics.global_relics.uncommon import QuestionCard, SingingBowl
from rooms.combat import CombatRoom
from tests.test_combat_utils import create_test_helper
from utils.types import RarityType, RoomType


def relic_ids(player: Player) -> list[str]:
    ids = []
    for relic in player.relics:
        assert isinstance(relic, Relic)
        ids.append(relic.idstr)
    return ids


@pytest.mark.parametrize('hp,loss,expected', [(30,10,30),(80,10,70),(1,80,1),(30,100,1)])
def test_max_hp_loss_only_clamps_current_hp(hp, loss, expected):
    h = create_test_helper()
    p = h.create_player(hp=hp, max_hp=80)
    LoseMaxHPAction(loss).execute()
    assert (p.hp, p.max_hp) == (expected, max(1,80-loss))


@pytest.mark.parametrize('relics,expected', [([],34),([MarkOfBloom],30),([MagicFlower],36),([MagicFlower,MarkOfBloom],30)])
def test_max_hp_gain_uses_normal_healing_rules(relics, expected):
    h = create_test_helper()
    p = h.create_player(hp=30, max_hp=80)
    p.relics = [r() for r in relics]
    h.start_combat([Cultist()])
    h.game_state.drive_actions()
    ModifyMaxHpAction(4).execute()
    h.game_state.drive_actions()
    assert (p.hp, p.max_hp) == (expected,84)


@pytest.mark.parametrize('parent_cls', [SlimeBoss, AcidSlimeL, SpikeSlimeL])
@pytest.mark.parametrize('residual', [1,10,35,65])
def test_real_damage_split_preserves_child_hp_and_allows_following_action(parent_cls, residual):
    h = create_test_helper()
    p = h.create_player(hp=1000,max_hp=1000,energy=3)
    random.seed(1024)
    parent = parent_cls()
    c = h.start_combat([parent])
    h.game_state.drive_actions()
    parent.max_hp = max(parent.max_hp, 2*(residual+6))
    parent.hp = residual+6
    card = Strike()
    p.card_manager.piles['hand'] = [card]
    h.game_state.add_action(PlayCardAction(card))
    h.game_state.drive_actions()
    assert parent.hp == residual
    assert parent.current_intention is not None and parent.current_intention.name == 'split'
    c.execute_enemy_phase()
    children = list(c.enemies)
    assert len(children) == 2 and parent not in children
    assert [(e.hp,e.max_hp) for e in children] == [(residual,residual)]*2
    assert c._check_combat_end() is None
    c._execute_next_phase()
    c._execute_next_phase()
    assert all(e.current_intention is not None for e in children)
    c._end_player_phase()
    c.execute_enemy_phase()
    assert all(len(e.history_intentions) == 1 for e in children)


@pytest.mark.parametrize('upgraded,damage', [(False,5),(True,7)])
def test_real_combust_reaches_end_turn_without_constructor_error(upgraded, damage):
    h = create_test_helper()
    p = h.create_player(hp=50,max_hp=80,energy=3)
    enemies = [Cultist(),Cultist()]
    c = h.start_combat(enemies)
    h.game_state.drive_actions()
    old = [e.hp for e in enemies]
    card = Combust()
    if upgraded:card.upgrade()
    p.card_manager.piles['hand'] = [card]
    h.game_state.add_action(PlayCardAction(card))
    h.game_state.drive_actions()
    c._end_player_phase()
    assert p.hp == 49
    assert [e.hp for e in enemies] == [hp-damage for hp in old]


@pytest.mark.parametrize('save,expected', [('none',0),('fairy',30),('tail',50)])
def test_combust_self_damage_reaches_death_or_real_save(save,expected):
    from potions.global_potions import FairyInABottle
    from relics.global_relics.rare import LizardTail
    from utils.result_types import GameTerminalState
    h = create_test_helper()
    p = h.create_player(hp=1,max_hp=100,energy=3)
    c = h.start_combat([Cultist()])
    h.game_state.drive_actions()
    fairy = FairyInABottle()
    tail = LizardTail()
    if save == 'fairy':p.potions.append(fairy)
    if save == 'tail':p.relics.append(tail)
    card = Combust()
    p.card_manager.piles['hand'] = [card]
    h.game_state.add_action(PlayCardAction(card))
    h.game_state.drive_actions()
    result = c._end_player_phase()
    assert p.hp == expected
    if save == 'none':assert result == GameTerminalState.GAME_LOSE
    if save == 'fairy':assert fairy not in p.potions
    if save == 'tail':assert not tail.can_revive


@pytest.mark.parametrize('roll,expected', [(0,RarityType.COMMON),(49,RarityType.COMMON),(50,RarityType.UNCOMMON),(82,RarityType.UNCOMMON),(83,RarityType.RARE),(99,RarityType.RARE)])
def test_elite_relic_tier_boundaries_use_live_pool(monkeypatch,roll,expected):
    h = create_test_helper()
    p = h.create_player()
    monkeypatch.setattr('random.randint',lambda *args:roll)
    AddEliteRelicAction().execute()
    h.game_state.drive_actions()
    assert len(p.relics) == 1
    relic = p.relics[0]
    assert isinstance(relic, Relic) and relic.rarity == expected
    assert relic.idstr in h.game_state.obtained_relics


def test_elite_relic_exhaustion_falls_through_and_excludes_owned(monkeypatch):
    from utils.registry import list_registered
    h = create_test_helper()
    p = h.create_player()
    h.game_state.obtained_relics.update(list_registered('relic'))
    monkeypatch.setattr('random.randint',lambda *args:0)
    AddEliteRelicAction().execute()
    assert relic_ids(p) == ['RedCirclet']


def test_elite_reward_excludes_held_relic_even_without_obtain_history(monkeypatch):
    from relics.character.ironclad import RedSkull
    h = create_test_helper()
    p = h.create_player()
    p.relics = [RedSkull()]
    monkeypatch.setattr('random.randint', lambda *args: 0)
    AddEliteRelicAction().execute()
    assert len(p.relics) == 2
    assert relic_ids(p)[1] != 'RedSkull'


@pytest.mark.parametrize('black_star', [False,True])
def test_elite_rewards_are_obtained_once_and_survive_next_combat(black_star):
    h = create_test_helper()
    p = h.create_player(hp=80,max_hp=80)
    p.relics = [BlackStar()] if black_star else []
    initial = len(p.relics)
    room = CombatRoom(enemies=[Cultist()],room_type=RoomType.ELITE)
    h.game_state.current_room = room
    room.init()
    h.game_state.add_actions(room._handle_victory())
    h.game_state.drive_actions()
    assert len(p.relics) == initial + (2 if black_star else 1)
    assert len(set(relic_ids(p))) == len(p.relics)
    obtained = relic_ids(p)
    room.leave()
    h.start_combat([Cultist()])
    h.game_state.drive_actions()
    assert relic_ids(p) == obtained


@pytest.mark.parametrize('room_type', [RoomType.MONSTER,RoomType.ELITE])
@pytest.mark.parametrize('modifiers,options', [([],3),([BustedCrown],1),([QuestionCard],4),([BustedCrown,QuestionCard],2)])
def test_prayer_wheel_separates_reward_amount_and_options(room_type,modifiers,options):
    from actions.card import ChooseObtainCardAction
    h = create_test_helper()
    p = h.create_player()
    p.relics = [PrayerWheel()]+[r() for r in modifiers]
    room = CombatRoom(enemies=[Cultist()],room_type=room_type)
    room.init()
    rewards = [a for a in room._handle_victory() if isinstance(a,ChooseObtainCardAction)]
    assert len(rewards) == (2 if room_type==RoomType.MONSTER else 1)
    assert [a.total for a in rewards] == [options]*len(rewards)


@pytest.mark.parametrize('bowl', [False,True])
def test_prayer_wheel_claims_both_actual_card_rewards(bowl):
    import cards.ironclad
    from cards.ironclad.defend import Defend
    h = create_test_helper()
    p = h.create_player(hp=40,max_hp=100)
    p.relics = [PrayerWheel()]+([SingingBowl()] if bowl else [])
    p.card_manager.piles['deck'] = [Strike(),Defend()]
    room = CombatRoom(enemies=[Cultist()],room_type=RoomType.MONSTER)
    h.game_state.current_room = room
    room.init()
    h.game_state.config.debug['select_type'] = 'last' if bowl else 'first'
    h.game_state.add_actions(room._handle_victory())
    h.game_state.drive_actions()
    assert len(p.card_manager.piles['deck']) == (2 if bowl else 4)
    assert (p.hp,p.max_hp) == ((44,104) if bowl else (40,100))
    room.leave()
    h.start_combat([Cultist()])
    h.game_state.drive_actions()
    assert len(p.card_manager.piles['deck']) == (2 if bowl else 4)
