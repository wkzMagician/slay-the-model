"""
Event 4 - The Shrine
"""
from events.base_event import Event
from actions.card import AddCardAction
from actions.display import SelectAction, DisplayTextAction
from actions.health import HealAction, LoseHPAction
from actions.reward import AddGoldAction
from events.event_pool import register_event
from localization import LocalStr

@register_event(
    event_id="the_shrine",
    floors='early',
    weight=100
)
class ShrineEvent(Event):
    """Visit shrine and make a sacrifice"""
    
    def trigger(self) -> str:
        """Trigger shrine event"""
        # Display event description
        from actions.display import DisplayTextAction
        self.action_queue.add_action(DisplayTextAction(
            text_key="events.the_shrine.description"
        ))
        
        # Build options
        options = []
        
        # Option 1: Sacrifice HP for max energy
        options.append(Option(
            name=LocalStr("events.the_shrine.option1"),
            actions=[
                LoseHPAction(amount=10),
                AddCardAction(pile="hand")
            ]
        ))
        
        # Option 2: Gain 100 gold
        options.append(Option(
            name=LocalStr("events.the_shrine.option2"),
            actions=[
                AddGoldAction(amount=100)
            ]
        ))
        
        # Option 3: Heal fully
        options.append(Option(
            name=LocalStr("events.the_shrine.option3"),
            actions=[
                HealAction(amount=999)
            ]
        ))
        
        # Display options and wait for selection
        self.action_queue.add_action(ChoiceAction(
            title=LocalStr("events.the_shrine.title"),
            options=options
        ))
        
        # End event after selection
        self.end_event()
        
        return None
