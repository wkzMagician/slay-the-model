"""Event: Cursed Tome - Act 2 Event

HP for random boss relic (book type).
"""

from utils.result_types import BaseResult, MultipleActionsResult
from events.base_event import Event
from events.event_pool import register_event
from actions.display import InputRequestAction, DisplayTextAction
from actions.reward import AddRandomRelicAction
from utils.types import RarityType
from actions.combat import LoseHPAction
from localization import LocalStr
from utils.option import Option
from engine.game_state import game_state


@register_event(event_id='cursed_tome', acts=[2], weight=100)
class CursedTome(Event):
    """
    Cursed Tome - HP for boss relic (book).
    
    Sequential state machine:
    - [Read] -> [Continue] Lose 1 HP -> repeat with 2 HP, 3 HP
    - After 3 reads: [Take] Lose 10 (15) HP -> Get Enchiridion/Nilry's Codex/Necronomicon
    - After 3 reads: [Stop] Lose 3 HP
    - [Leave] Nothing happens (available at any time)
    """
    
    # Boss relics that are "books" (card manipulation powers)
    BOOK_RELICS = ['Enchiridion', "Nilry's Codex", 'Necronomicon']
    
    def __init__(self):
        super().__init__()
        self.read_count = 0
    
    def trigger(self) -> BaseResult:
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.cursed_tome.description'
        ))
        
        # HP cost for Take: 10 normal, 15 on A15+
        take_hp_cost = 15 if game_state.ascension >= 15 else 10
        
        # Build options based on state
        options = []
        
        if self.read_count < 3:
            # Reading phase: show Continue option
            read_hp = self.read_count + 1  # 1, 2, 3
            options.append(Option(
                name=LocalStr('events.cursed_tome.continue'),
                actions=[LoseHPAction(amount=read_hp)]
            ))
            # Increment read count for next trigger
            self.read_count += 1
        else:
            # After 3 reads, show Take and Stop options
            # Take: Get a random book boss relic
            options.append(Option(
                name=LocalStr('events.cursed_tome.take'),
                actions=[
                    LoseHPAction(amount=take_hp_cost),
                    AddRandomRelicAction(
                        pool=self.BOOK_RELICS,
                        rarities=[RarityType.BOSS]
                    )
                ]
            ))
            # Stop: Just lose 3 HP
            options.append(Option(
                name=LocalStr('events.cursed_tome.stop'),
                actions=[LoseHPAction(amount=3)]
            ))
        
        # Leave option always available
        options.append(Option(
            name=LocalStr('events.cursed_tome.leave'),
            actions=[]
        ))
        
        actions.append(InputRequestAction(
            title=LocalStr('events.cursed_tome.title'),
            options=options
        ))
        
        # Only end event when player makes final decision (Take/Stop/Leave)
        # Continue option should NOT end the event
        # Note: The action system will re-trigger this event for Continue
        # For final options, we need to detect which option was selected
        # Since we can't know the selection here, we use a different approach:
        # - Continue: doesn't call end_event (event persists)
        # - Take/Stop/Leave: should call end_event
        
        # Actually, the event system calls trigger() for each selection.
        # After Continue, the event is re-triggered with updated read_count.
        # After Take/Stop/Leave, we should end the event.
        
        # For now, end the event - the state machine works by re-triggering
        # after Continue selections (read_count is preserved in event instance)
        if self.read_count > 3:
            # After Take/Stop/Leave, end event
            self.end_event()
        
        return MultipleActionsResult(actions)
