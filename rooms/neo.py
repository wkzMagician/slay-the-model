"""
Neo reward room - starting room where player chooses their blessing.
"""
from actions.display import DisplayTextAction
from tui.print_utils import tui_print
from utils.result_types import GameStateResult, NoneResult, MultipleActionsResult
from rooms.base import Room, BaseResult
from utils.registry import register


@register("room")
class NeoRewardRoom(Room):
    """Neo reward blessing room - the starting room"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.room_type = None  # Special room, doesn't have standard type

    def init(self):
        """Initialize Neo room - no special initialization needed"""

    def enter(self) -> BaseResult:
        """Enter Neo room and trigger blessing selection"""
        from engine.game_state import game_state
        from utils.result_types import MultipleActionsResult
        from localization import t
        actions = []

        # Display welcome message directly
        tui_print("\n" + "=" * 60)
        tui_print(t("ui.neo_welcome", default="Welcome, traveler. I am Neow."))
        tui_print(t("ui.neo_intro", default="I shall grant you a blessing to begin your journey."))
        tui_print("=" * 60 + "\n")

        # Create and trigger Neo event
        from events.neo_event import NeoEvent
        neo_event = NeoEvent()

        # Execute Neo event
        result = neo_event.trigger()

        if isinstance(result, GameStateResult):
            return result

        # Display goodbye message directly
        tui_print("\n" + t("ui.neo_goodbye", default="Your journey begins now. Good luck!"))
        tui_print("=" * 60 + "\n")

        # Neo room is done, player should leave
        self.should_leave = True

        # Return all actions to be executed
        if actions:
            return MultipleActionsResult(actions)
        return NoneResult()
