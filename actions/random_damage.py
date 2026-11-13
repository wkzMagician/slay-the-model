"""Deferred target selection for power and lightning damage."""
from actions.base import Action
from actions.combat_damage import DealDamageAction
from engine.random_streams import get_rng
from engine.runtime_api import add_action, add_actions
from utils.registry import register
from utils.types import DamageType


def _living_enemies():
    from engine.game_state import game_state

    combat = game_state.current_combat
    if combat is None:
        return []
    return [enemy for enemy in combat.enemies
            if not enemy.is_dead() and not enemy.half_dead
            and not getattr(enemy, "is_escaping", False)
            and not getattr(enemy, "is_dying", False)]


@register("action")
class DamageRandomEnemyAction(Action):
    preserve_after_combat = True

    def __init__(self, damage: int, source=None):
        self.damage = damage
        self.source = source

    def execute(self) -> None:
        enemies = _living_enemies()
        if not enemies:
            return
        target = enemies[get_rng("card_random").randint(0, len(enemies) - 1)]
        add_action(DealDamageAction(
            damage=self.damage, target=target, source=self.source,
            damage_type=DamageType.THORNS,
        ), to_front=True)


@register("action")
class LightningDamageAction(Action):
    preserve_after_combat = True

    def __init__(self, damage: int, hit_all: bool, source=None):
        self.damage = damage
        self.hit_all = hit_all
        self.source = source

    def execute(self) -> None:
        enemies = _living_enemies()
        if not enemies:
            return
        if not self.hit_all:
            enemies = [enemies[get_rng("card_random").randint(0, len(enemies) - 1)]]
        actions = []
        for target in enemies:
            damage = int(self.damage * 1.5) if target.get_power("Lock-On") is not None else self.damage
            actions.append(DealDamageAction(
                damage=damage, target=target, source=self.source,
                damage_type=DamageType.THORNS,
            ))
        if self.hit_all:
            # An original DamageAllEnemiesAction completes its matrix before
            # queued reactions run between separate damage actions.
            for action in actions:
                action.execute()
        else:
            add_actions(actions, to_front=True)
