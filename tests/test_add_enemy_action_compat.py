from actions.combat import AddEnemyAction
from enemies.act2.the_collector import TheCollector, TorchHead
from engine.combat import Combat
from engine.game_state import game_state


def test_add_enemy_action_accepts_enemy_class_and_spawns_instance():
    combat = Combat(enemies=[TheCollector()])
    game_state.current_combat = combat

    action = AddEnemyAction(TorchHead)
    result = action.execute()

    assert result is not None
    assert any(isinstance(enemy, TorchHead) for enemy in combat.enemies)
