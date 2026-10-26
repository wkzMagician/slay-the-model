"""Selective cleanup at the same death boundaries as clearPostCombatActions."""


def clear_post_combat_actions_if_finished() -> None:
    from engine.game_state import game_state

    combat = game_state.current_combat
    if combat is None or not combat.enemies:
        return
    # A half-dead phase is still part of combat. Linked groups determine their
    # own final death; HP alone must not end the encounter.
    if not all(enemy.is_dead() for enemy in combat.enemies):
        return
    # Filter only actions already queued at this boundary. Retained actions
    # may legitimately add ordinary follow-ups later (e.g. card exhaust hooks).
    queue = game_state.action_queue
    queue.queue = [action for action in queue.queue
                   if getattr(action, "preserve_after_combat", False)]
