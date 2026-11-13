from actions.random_damage import LightningDamageAction
from engine.runtime_api import add_action
from orbs.base import Orb
from utils.dynamic_values import resolve_orb_value
from utils.types import TargetType


class LightningOrb(Orb):
    passive_timing = "turn_end"
    target_type = TargetType.ENEMY_RANDOM

    def __init__(self):
        self.passive_damage = 3
        self.evoke_damage = 8

    def _queue_damage(self, base_damage: int, *, to_front: bool):
        from engine.game_state import game_state

        player = game_state.player
        if player is None:
            return
        add_action(LightningDamageAction(
            damage=resolve_orb_value(base_damage),
            hit_all=player.get_power("Electro") is not None,
            source=player,
        ), to_front=to_front)

    def on_passive(self) -> None:
        self._queue_damage(self.passive_damage, to_front=False)

    def on_evoke(self) -> None:
        self._queue_damage(self.evoke_damage, to_front=True)
