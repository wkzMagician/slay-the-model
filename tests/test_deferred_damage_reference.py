"""Actual original target actions with an explicitly prepared damage boundary."""
import gzip
import json
from pathlib import Path
from typing import cast

import pytest

from actions.combat_damage import DealDamageAction
from actions.random_damage import DamageRandomEnemyAction, LightningDamageAction
from enemies.base import Enemy
from engine.combat import Combat
from engine.game_state import game_state
from engine.random_streams import DOMAINS, StreamRandom, get_rng
from powers.definitions.lock_on import LockOnPower
from tests.test_special_card_reference import trace_rng
from utils.types import DamageType

FIXTURE = Path(__file__).parent / "fixtures/deferred_damage_reference.json.gz"
ROWS = json.loads(gzip.decompress(FIXTURE.read_bytes()))


class PreparedEnemy(Enemy):
    prepared_half_dead = False

    @property
    def half_dead(self):
        return self.prepared_half_dead

    def is_dead(self):
        return not self.prepared_half_dead and super().is_dead()


@pytest.mark.parametrize("row", ROWS)
def test_original_deferred_actions_targets_damage_calls_and_state(row, monkeypatch):
    player = game_state.player
    player.relics.clear()
    enemies = []
    for value in row["enemies"]:
        enemy = PreparedEnemy(max_hp=1000)
        enemy.hp = value["hp"]
        enemy.block = value["block"]
        enemy.prepared_half_dead = value["half_dead"]
        enemy.is_escaping = value["escaping"]
        enemy.is_dying = value["dying"]
        if value["lock"]:
            enemy.add_power(LockOnPower(amount=1, owner=enemy))
        enemies.append(enemy)
    # This is a prepared component arena with no combat initialization hooks.
    game_state.combat = Combat(enemies=enemies)
    rng = cast(StreamRandom, get_rng("card_random"))
    rng.seed(int(row["seed"]))
    calls = trace_rng(rng, monkeypatch)
    others = {name: cast(StreamRandom, get_rng(name)).export_state() for name in DOMAINS if name != "card_random"}
    hits = []
    original = DealDamageAction.execute

    def execute(action):
        assert action.damage_type == DamageType.THORNS
        hits.append([next(index for index, enemy in enumerate(enemies) if enemy is action.target), action.damage])
        return original(action)

    monkeypatch.setattr(DealDamageAction, "execute", execute)
    if row["pre_damage"]:
        game_state.add_action(DealDamageAction(
            damage=row["pre_damage"], target=enemies[0], source=player, damage_type=DamageType.THORNS,
        ))
    for _ in range(row["count"]):
        if row["kind"] == "juggernaut":
            action = DamageRandomEnemyAction(damage=row["damage"], source=player)
        else:
            action = LightningDamageAction(damage=row["damage"], hit_all=row["hit_all"], source=player)
        game_state.add_action(action)
    assert calls == []
    assert game_state.drive_actions() is None
    assert hits == row["hits"]
    assert [enemy.hp for enemy in enemies] == row["health"]
    assert [enemy.block for enemy in enemies] == row["blocks"]
    assert calls == row["calls"]
    state = rng.export_state()
    assert {key: state[key] for key in row["state"]} == row["state"]
    assert others == {name: cast(StreamRandom, get_rng(name)).export_state() for name in others}
