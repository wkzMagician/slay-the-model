"""Event: Ancient Writing - Act 2 Event

A choice event where you can remove a card or upgrade all Strikes and Defends.
"""
from engine.runtime_api import add_action, add_actions, publish_message, request_input, set_terminal_state

from events.base_event import Event
from events.event_pool import register_event
from actions.display import InputRequestAction, DisplayTextAction
from actions.card import ChooseRemoveCardAction
from actions.base import LambdaAction
from localization import LocalStr
from utils.option import Option


@register_event(category='event', event_id='ancient_writing', acts=[2], weight=100)
class AncientWriting(Event):
    """Ancient Writing - remove card or upgrade Strikes/Defends."""
    
    def trigger(self) -> None:
        from engine.game_state import game_state
        
        def upgrade_all_strikes_and_defends():
            """Upgrade all Strike and Defend cards in the player's deck."""
            player = game_state.player
            upgraded_count = 0
            for card in player.deck:
                # Check if card is a Strike or Defend (by class name or instance check)
                if 'Strike' in card.__class__.__name__ or 'Defend' in card.__class__.__name__:
                    if card.can_upgrade():
                        card.upgrade()
                        upgraded_count += 1
        
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.ancient_writing.description'
        ))
        
        # Build options
        options = [
            Option(
                name=LocalStr('events.ancient_writing.elegance'),
                detail=LocalStr('events.ancient_writing.elegance_detail'),
                actions=[ChooseRemoveCardAction()]
            ),
            Option(
                name=LocalStr('events.ancient_writing.simplicity'),
                detail=LocalStr('events.ancient_writing.simplicity_detail'),
                # Upgrade ALL Strike and Defend cards in deck
                actions=[LambdaAction(upgrade_all_strikes_and_defends)]
            )
        ]
        
        actions.append(InputRequestAction(
            title=LocalStr('events.ancient_writing.title'),
            options=options
        ))
        
        self.end_event()
        from engine.game_state import game_state
        add_actions(actions)
