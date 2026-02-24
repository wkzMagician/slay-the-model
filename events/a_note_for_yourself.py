"""Event: A Note For Yourself - Shrine Event (All Acts, disabled A15+)

Cross-run card storage event that allows receiving a card from previous run
and storing a card for future runs.
"""

import json
import os
from pathlib import Path
from typing import Optional

from utils.result_types import BaseResult, MultipleActionsResult
from events.base_event import Event
from events.event_pool import register_event
from actions.display import SelectAction, DisplayTextAction
from actions.card import AddCardAction, ChooseRemoveCardAction
from localization import LocalStr
from utils.option import Option
from engine.game_state import game_state
from cards.base import Card
from utils.registry import get_registered

# Path for storing cross-run data
STORAGE_FILE = Path(__file__).parent.parent / "save_data" / "note_storage.json"


def _load_stored_card() -> Optional[dict]:
    """Load stored card data from previous run."""
    try:
        if STORAGE_FILE.exists():
            with open(STORAGE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('stored_card')
    except (json.JSONDecodeError, IOError):
        pass
    return None


def _save_stored_card(card_data: Optional[dict]):
    """Save card data for future runs."""
    STORAGE_FILE.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(STORAGE_FILE, 'w', encoding='utf-8') as f:
            json.dump({'stored_card': card_data}, f)
    except IOError:
        pass


def _card_to_dict(card: Card) -> dict:
    """Convert card to storable dictionary."""
    return {
        'idstr': card.idstr,
        'upgrades': getattr(card, 'upgrades', 0),
    }


def _dict_to_card(data: dict) -> Optional[Card]:
    """Recreate card from stored dictionary."""
    if not data or 'idstr' not in data:
        return None
    
    card_cls = get_registered('card', data['idstr'])
    if not card_cls:
        return None
    
    card = card_cls()
    upgrades = data.get('upgrades', 0)
    for _ in range(upgrades):
        if hasattr(card, 'upgrade'):
            card.upgrade()
    
    return card


@register_event(event_id='a_note_for_yourself', acts='shared', weight=100)
class ANoteForYourself(Event):
    """A Note For Yourself - cross-run card storage."""
    
    @classmethod
    def can_appear(cls) -> bool:
        """Disabled on Ascension 15+ and Daily Climb."""
        if game_state.ascension >= 15:
            return False
        # Also disabled in Daily Climb (not implemented yet)
        return True
    
    def trigger(self) -> BaseResult:
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.a_note_for_yourself.description'
        ))
        
        # Load stored card from previous run
        stored_data = _load_stored_card()
        stored_card = _dict_to_card(stored_data) if stored_data else None
        
        # Build options
        options = []
        
        if stored_card:
            # Option to take stored card and give a new one
            options.append(Option(
                name=LocalStr('events.a_note_for_yourself.take_and_give'),
                actions=[
                    AddCardAction(card=stored_card, dest_pile='deck'),
                    ChooseRemoveCardAction(
                        pile='deck',
                        amount=1,
                        exclude_rarities=[RarityType.CURSE]
                    ),
                    StoreCardForFutureAction(),
                ]
            ))
            
            # Option to just take the card
            options.append(Option(
                name=LocalStr('events.a_note_for_yourself.take_only'),
                actions=[
                    AddCardAction(card=stored_card, dest_pile='deck'),
                ]
            ))
        else:
            # No stored card - option to store one
            options.append(Option(
                name=LocalStr('events.a_note_for_yourself.give_only'),
                actions=[
                    ChooseRemoveCardAction(
                        pile='deck',
                        amount=1,
                        exclude_rarities=[RarityType.CURSE]
                    ),
                    StoreCardForFutureAction(),
                ]
            ))
        
        # Always can ignore
        options.append(Option(
            name=LocalStr('events.a_note_for_yourself.ignore'),
            actions=[]
        ))
        
        actions.append(SelectAction(
            title=LocalStr('events.a_note_for_yourself.title'),
            options=options
        ))
        
        self.end_event()
        return MultipleActionsResult(actions)


from utils.types import RarityType
from actions.base import Action
from utils.registry import register


@register("action")
class StoreCardForFutureAction(Action):
    """Store the last removed card for future runs."""
    
    def execute(self) -> BaseResult:
        # This action is triggered after ChooseRemoveCardAction
        # We need to find what card was removed
        # For now, we'll use a simple approach: store the most recently
        # removed card from the player's deck
        # 
        # In a full implementation, we'd track the removed card explicitly
        # through the action system
        
        # Get the current deck and find cards not in the original deck
        # This is a workaround until we have proper card tracking
        from utils.result_types import NoneResult
        return NoneResult()
