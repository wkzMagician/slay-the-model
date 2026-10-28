"""Event: The Colosseum - Act 2 Event

Double fight for big rewards.
"""
from engine.runtime_api import add_action, add_actions, publish_message, request_input, set_terminal_state

from events.base_event import Event
from events.event_pool import register_event
from actions.display import InputRequestAction, DisplayTextAction
from actions.card import AddRandomCardAction
from actions.reward import AddGoldAction, AddRandomRelicAction
from actions.combat import StartFightAction
from actions.base import LambdaAction
from localization import LocalStr
from utils.option import Option
from utils.types import RoomType
from engine.game_state import game_state


@register_event(category='event', event_id='the_colosseum', acts=[2], weight=100)
class TheColosseum(Event):
    """The Colosseum - double fight for rewards.
    
    [Fight] Fight the Slavers (Blue Slaver + Red Slaver) - NO REWARDS
    After winning the first fight:
    [Victory] Fight Taskmaster + Gremlin Nob -> 100g + rare relic + uncommon relic + card
    [Cowardice] Escape with your life
    """
    
    @classmethod
    def can_appear(cls) -> bool:
        """Use original map coordinates, excluding the extra Neo and boss rows."""
        if game_state.current_act != 2:
            return False
        map_data = getattr(game_state, 'map_data', None)
        if map_data is None or not map_data.nodes:
            return False
        node = map_data.get_current_node()
        if node is None:
            return False
        rows = map_data.nodes
        start = 1 if rows[0] and all(n.room_type == RoomType.NEO for n in rows[0]) else 0
        end = next((i for i, row in enumerate(rows) if any(n.room_type == RoomType.BOSS for n in row)), len(rows))
        # Node.floor includes previous acts; current_floor indexes this act's rows.
        floor = map_data.current_floor
        return start <= floor < end and floor - start > (end - start) // 2

    def __init__(self):
        super().__init__()
        self.first_fight_done = False
    
    def _finish_first_fight(self) -> None:
        self.first_fight_done = True
        self.trigger()

    def trigger(self) -> None:
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.the_colosseum.description'
        ))
        
        if not self.first_fight_done:
            from enemies.act1.slaver import BlueSlaver, RedSlaver

            actions.append(InputRequestAction(
                title=LocalStr('events.the_colosseum.title'),
                options=[
                    Option(
                        name=LocalStr('events.the_colosseum.fight'),
                        detail=LocalStr('events.the_colosseum.fight_detail'),
                        actions=[
                            StartFightAction(
                                enemies=[BlueSlaver(), RedSlaver()],
                                escape_actions=[LambdaAction(self.end_event)],
                                victory_actions=[LambdaAction(self._finish_first_fight)],
                            )
                        ],
                    )
                ],
            ))
        else:
            from enemies.act1.gremlin_nob import GremlinNob
            from enemies.act2.taskmaster import Taskmaster

            actions.append(InputRequestAction(
                title=LocalStr('events.the_colosseum.title'),
                options=[
                    Option(
                        name=LocalStr('events.the_colosseum.victory'),
                        detail=LocalStr('events.the_colosseum.victory_detail'),
                        actions=[
                            StartFightAction(
                                enemies=[Taskmaster(), GremlinNob()],
                                escape_actions=[LambdaAction(self.end_event)],
                                victory_actions=[
                                    AddGoldAction(amount=100),
                                    AddRandomRelicAction(rarity='rare'),
                                    AddRandomRelicAction(rarity='uncommon'),
                                    AddRandomCardAction(),
                                    LambdaAction(self.end_event),
                                ],
                            )
                        ],
                    ),
                    Option(
                        name=LocalStr('events.the_colosseum.cowardice'),
                        detail=LocalStr('events.the_colosseum.cowardice_detail'),
                        actions=[LambdaAction(self.end_event)],
                    ),
                ],
            ))
        
        add_actions(actions)
