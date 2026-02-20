"""Event: The Colosseum - Act 2 Event

Double fight for big rewards.
"""

from utils.result_types import BaseResult, MultipleActionsResult
from events.base_event import Event
from events.event_pool import register_event
from actions.display import SelectAction, DisplayTextAction
from actions.card import AddRandomCardAction
from actions.reward import AddGoldAction, AddRandomRelicAction
from actions.combat import StartFightAction
from localization import LocalStr
from utils.option import Option
from engine.game_state import game_state


@register_event(event_id='the_colosseum', floors='mid', weight=100)
class TheColosseum(Event):
    """The Colosseum - double fight for rewards."""
    
    @classmethod
    def can_appear(cls) -> bool:
        """Only appears on Floor 7+ of Act 2."""
        return game_state.current_floor >= 7 and game_state.ascension >= 15
    
    def __init__(self):
        super().__init__()
        self.first_fight_done = False
    
    def trigger(self) -> BaseResult:
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.the_colosseum.description'
        ))
        
        # Build options
        options = []
        
        if not self.first_fight_done:
            options.append(Option(
                name=LocalStr('events.the_colosseum.fight'),
                actions=[
                    StartFightAction(enemies=['blue_slaver', 'red_slaver'])
                ]
            ))
            self.first_fight_done = True
        else:
            # After first fight, can continue or flee
            options.extend([
                Option(
                    name=LocalStr('events.the_colosseum.victory'),
                    actions=[
                        StartFightAction(enemies=['taskmaster', 'gremlin_nob']),
                        AddGoldAction(amount=100),
                        AddRandomRelicAction(rarity='rare'),
                        AddRandomRelicAction(rarity='uncommon'),
                        AddRandomCardAction()
                    ]
                ),
                Option(
                    name=LocalStr('events.the_colosseum.cowardice'),
                    actions=[]
                )
            ])
        
        options.append(Option(
            name=LocalStr('events.the_colosseum.leave'),
            actions=[]
        ))
        
        actions.append(SelectAction(
            title=LocalStr('events.the_colosseum.title'),
            options=options
        ))
        
        self.end_event()
        return MultipleActionsResult(actions)
