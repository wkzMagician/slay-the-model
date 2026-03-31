from engine.runtime_api import add_action
from actions.combat import DealDamageAction
from entities.creature import Creature
from orbs.base import Orb
from utils.combat import resolve_target
from utils.dynamic_values import resolve_orb_damage
from utils.types import TargetType


class LightningOrb(Orb):
    passive_timing = "turn_end"
    target_type = TargetType.ENEMY_RANDOM

    def __init__(self):
        self.passive_damage = 3
        self.evoke_damage = 8

    def _resolve_enemies(self) -> list[Creature]:
        from engine.game_state import game_state

        if game_state.player is not None and game_state.player.get_power("Electro") is not None:
            if game_state.current_combat is None:
                return []
            return [enemy for enemy in game_state.current_combat.enemies if enemy.is_alive]
        targets = resolve_target(self.target_type)
        if not targets:
            return []
        target = targets[0]
        return [target] if target is not None else []

    def on_passive(self) -> None:
        for target in self._resolve_enemies():
            add_action(DealDamageAction(damage=resolve_orb_damage(self.passive_damage, target), target=target, damage_type="magic"))

    def on_evoke(self) -> None:
        for target in self._resolve_enemies():
            add_action(DealDamageAction(damage=resolve_orb_damage(self.evoke_damage, target), target=target, damage_type="magic"))
