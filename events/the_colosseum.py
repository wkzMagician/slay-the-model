"""Event: The Colosseum - Act 2 Event

Double fight for big rewards.
"""

from utils.result_types import BaseResult, MultipleActionsResult
from events.base_event import Event
from events.event_pool import register_event
from actions.display import InputRequestAction, DisplayTextAction
from actions.card import AddRandomCardAction
from actions.reward import AddGoldAction, AddRandomRelicAction
from actions.combat import StartFightAction
from actions.base import LambdaAction
from utils.registry import get_registered
from localization import LocalStr
from utils.option import Option
from engine.game_state import game_state


@register_event(event_id='the_colosseum', acts=[2], weight=100)
class TheColosseum(Event):
    """The Colosseum - double fight for rewards.
    
    [Fight] Fight the Slavers (Blue Slaver + Red Slaver) - NO REWARDS
    After winning the first fight:
    [Victory] Fight Taskmaster + Gremlin Nob -> 100g + rare relic + uncommon relic + card
    [Cowardice] Escape with your life
    [Leave] Always available - Leave the arena
    """
    
    @classmethod
    def can_appear(cls) -> bool:
        """Only appears on Floor 7+ of Act 2."""
        # Colosseum appears on Floor 7+ of Act 2
        # Note: In original game, this is Floor 7+ regardless of ascension
        return game_state.current_act == 2 and game_state.floor_in_act >= 7
    
    def __init__(self):
        super().__init__()
        self.first_fight_done = False
    
    def trigger(self) -> BaseResult:
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.the_colosseum.description'
        ))
        
        # Build options based on current state
        options = []
        
        if not self.first_fight_done:
            # Create Slavers for first fight
            blue_slaver_class = get_registered("enemy", 'blue_slaver')
            red_slaver_class = get_registered("enemy", 'red_slaver')
            slavers = []
            if blue_slaver_class:
                slavers.append(blue_slaver_class())
            if red_slaver_class:
                slavers.append(red_slaver_class())
            
            # Initial state: Show Fight and Leave options
            # First fight has no rewards, just sets first_fight_done = True after victory
            options.append(Option(
                name=LocalStr('events.the_colosseum.fight'),
                actions=[
                    StartFightAction(
                        enemies=slavers,
                        victory_actions=[
                            LambdaAction(lambda: setattr(self, 'first_fight_done', True))
                        ]
                    )
                ]
            ))
            # Leave option - end event immediately
            options.append(Option(
                name=LocalStr('events.the_colosseum.leave'),
                actions=[LambdaAction(lambda: self.end_event())]
            ))
            # Don't call end_event() here - event resumes after Fight
        else:
            # Create enemies for second fight
            taskmaster_class = get_registered("enemy", 'taskmaster')
            gremlin_nob_class = get_registered("enemy", 'gremlin_nob')
            second_fight_enemies = []
            if taskmaster_class:
                second_fight_enemies.append(taskmaster_class())
            if gremlin_nob_class:
                second_fight_enemies.append(gremlin_nob_class())
            
            # After first fight won: Show Victory and Cowardice options
            # Second fight gives big rewards on victory
            options.extend([
                Option(
                    name=LocalStr('events.the_colosseum.victory'),
                    actions=[
                        StartFightAction(
                            enemies=second_fight_enemies,
                            victory_actions=[
                                AddGoldAction(amount=100),
                                AddRandomRelicAction(rarity='rare'),
                                AddRandomRelicAction(rarity='uncommon'),
                                AddRandomCardAction(),
                                LambdaAction(lambda: self.end_event())
                            ]
                        )
                    ]
                ),
                Option(
                    name=LocalStr('events.the_colosseum.cowardice'),
                    actions=[LambdaAction(lambda: self.end_event())]
                )
            ])
        
        actions.append(InputRequestAction(
            title=LocalStr('events.the_colosseum.title'),
            options=options
        ))
        
        return MultipleActionsResult(actions)
