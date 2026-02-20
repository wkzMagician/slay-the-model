"""Orb-related actions."""

from actions.base import Action
from utils.result_types import BaseResult, NoneResult, MultipleActionsResult
from utils.registry import register


@register("action")
class OrbPassiveAction(Action):
    """Trigger an orb's passive effect

    Required:
        orb: Orb instance to trigger passive for

    Optional:
        None
    """
    def __init__(self, orb):
        self.orb = orb

    def execute(self) -> 'BaseResult':
        """Execute the orb's passive effect"""
        if not self.orb:
            return NoneResult()

        # Get actions from orb's passive
        actions = self.orb.on_passive()

        if actions:
            if isinstance(actions, list):
                return MultipleActionsResult(actions)
            return MultipleActionsResult([actions])

        return NoneResult()


@register("action")
class OrbEvokeAction(Action):
    """Trigger an orb's evoke effect

    Required:
        orb: Orb instance to evoke

    Optional:
        None
    """
    def __init__(self, orb):
        self.orb = orb

    def execute(self) -> 'BaseResult':
        """Execute the orb's evoke effect"""
        if not self.orb:
            return NoneResult()

        # Get actions from orb's evoke
        actions = self.orb.on_evoke()

        if actions is None:
            return NoneResult()
        
        if isinstance(actions, list):
            return MultipleActionsResult(actions)
        return MultipleActionsResult([actions])


@register("action")
class TriggerOrbPassivesAction(Action):
    """Trigger passives for all orbs with matching timing

    Required:
        timing (str): Timing to trigger ("turn_start", "turn_end", etc.)

    Optional:
        None
    """
    def __init__(self, timing: str):
        self.timing = timing

    def execute(self) -> 'BaseResult':
        """Trigger passives for all matching orbs"""
        from engine.game_state import game_state

        if not game_state.player or not hasattr(game_state.player, 'orb_manager'):
            return NoneResult()

        actions_to_return = []

        # Get all orbs
        orbs = list(game_state.player.orb_manager.orbs)

        # Trigger passives for matching timing
        for orb in orbs:
            if getattr(orb, "passive_timing", None) == self.timing:
                action = OrbPassiveAction(orb=orb)
                actions_to_return.append(action)

        if actions_to_return:
            return MultipleActionsResult(actions_to_return)

        return NoneResult()


@register("action")
class EvokeOrbAction(Action):
    """Evoke an orb from player's orb slots

    Required:
        index (int): Orb index to evoke (default 0 for leftmost)

    Optional:
        times (int): Number of times to evoke (default 1)
    """
    def __init__(self, index: int = 0, times: int = 1):
        self.index = index
        self.times = times

    def execute(self) -> 'BaseResult':
        """Evoke the orb at the specified index"""
        from engine.game_state import game_state

        if not game_state.player or not hasattr(game_state.player, 'orb_manager'):
            return NoneResult()

        orb_manager = game_state.player.orb_manager
        orbs = list(orb_manager.orbs)

        # Validate index
        if self.index < 0 or self.index >= len(orbs):
            return NoneResult()

        orb = orbs[self.index]

        # Evoke the orb (remove it)
        actions = []
        for _ in range(self.times):
            evoke_action = OrbEvokeAction(orb=orb)
            actions.append(evoke_action)

        # Remove the orb from manager
        orb_manager.remove_orb(self.index)

        if actions:
            return MultipleActionsResult(actions)

        return NoneResult()


@register("action")
class EvokeAllOrbsAction(Action):
    """Evoke all orbs from player's orb slots

    Required:
        None

    Optional:
        None
    """
    def __init__(self):
        pass

    def execute(self) -> 'BaseResult':
        """Evoke all orbs"""
        from engine.game_state import game_state

        if not game_state.player or not hasattr(game_state.player, 'orb_manager'):
            return NoneResult()

        orb_manager = game_state.player.orb_manager
        orbs = list(orb_manager.orbs)

        if not orbs:
            return NoneResult()

        # Create evoke actions for all orbs
        actions = []
        for orb in orbs:
            evoke_action = OrbEvokeAction(orb=orb)
            actions.append(evoke_action)

        # Clear all orbs from manager
        orb_manager.clear_all()

        if actions:
            return MultipleActionsResult(actions)

        return NoneResult()


@register("action")
class AddOrbAction(Action):
    """Add an orb to player's orb slots

    Required:
        orb: Orb instance to add

    Optional:
        None
    """
    def __init__(self, orb):
        self.orb = orb

    def execute(self) -> 'BaseResult':
        """Add the orb to player's orb manager"""
        from engine.game_state import game_state

        if not game_state.player or not hasattr(game_state.player, 'orb_manager'):
            return NoneResult()

        orb_manager = game_state.player.orb_manager

        # If max slots exceeded, evoke rightmost orb first
        if len(orb_manager.orbs) >= orb_manager.max_orb_slots:
            # Evoke the rightmost orb
            evoke_action = EvokeOrbAction(index=-1)
            evoke_action.execute()

        # Add the new orb
        orb_manager.add_orb(self.orb)

        return NoneResult()