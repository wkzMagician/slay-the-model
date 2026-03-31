"""Orb-related actions."""
from engine.runtime_api import add_actions

from actions.base import Action
from utils.registry import register


@register("action")
class OrbPassiveAction(Action):
    def __init__(self, orb):
        self.orb = orb

    def execute(self) -> None:
        if self.orb:
            self.orb.on_passive()


@register("action")
class OrbEvokeAction(Action):
    def __init__(self, orb):
        self.orb = orb

    def execute(self) -> None:
        if self.orb:
            self.orb.on_evoke()


@register("action")
class EvokeOrbAction(Action):
    def __init__(self, index: int = 0, times: int = 1):
        self.index = index
        self.times = times

    def execute(self) -> None:
        from engine.game_state import game_state

        if not game_state.player or not hasattr(game_state.player, "orb_manager"):
            return

        orb_manager = game_state.player.orb_manager
        orbs = list(orb_manager.orbs)
        orb_index = self.index
        if orb_index < 0:
            orb_index = len(orbs) + orb_index
        if orb_index < 0 or orb_index >= len(orbs):
            return

        orb = orbs[orb_index]
        actions = [OrbEvokeAction(orb=orb) for _ in range(self.times)]
        orb_manager.remove_orb(orb_index)
        add_actions(actions, to_front=True)


@register("action")
class EvokeAllOrbsAction(Action):
    def execute(self) -> None:
        from engine.game_state import game_state

        if not game_state.player or not hasattr(game_state.player, "orb_manager"):
            return

        orbs = list(game_state.player.orb_manager.orbs)
        if not orbs:
            return

        game_state.player.orb_manager.clear_all()
        add_actions([OrbEvokeAction(orb=orb) for orb in orbs], to_front=True)


@register("action")
class AddOrbAction(Action):
    def __init__(self, orb):
        self.orb = orb

    def execute(self) -> None:
        from engine.game_state import game_state

        if not game_state.player or not hasattr(game_state.player, "orb_manager"):
            return

        orb_manager = game_state.player.orb_manager
        if len(orb_manager.orbs) >= orb_manager.max_orb_slots:
            EvokeOrbAction(index=-1).execute()

        orb_manager.add_orb(self.orb)
        if game_state.current_combat is not None:
            orb_name = self.orb.__class__.__name__.replace("Orb", "")
            history = game_state.current_combat.combat_state.orb_history
            history[orb_name] = history.get(orb_name, 0) + 1


@register("action")
class IncreaseOrbSlotsAction(Action):
    def __init__(self, amount: int):
        self.amount = amount

    def execute(self) -> None:
        from engine.game_state import game_state

        if not game_state.player or not hasattr(game_state.player, "orb_manager"):
            return

        game_state.player.orb_manager.max_orb_slots += self.amount
