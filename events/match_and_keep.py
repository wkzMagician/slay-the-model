"""Event: Match and Keep - Shrine Event (All Acts)

A card matching minigame where you flip cards and match pairs to add them to your deck.
"""
from engine.runtime_api import add_action, add_actions, publish_message, request_input, set_terminal_state

import random
from typing import List, Optional, Tuple
from events.base_event import Event
from events.event_pool import register_event
from actions.display import InputRequestAction, DisplayTextAction
from actions.card import AddCardAction
from actions.base import Action
from utils.registry import get_registered, register
from localization import LocalStr
from utils.option import Option
from engine.game_state import game_state
from cards.base import Card
from utils.registry import get_registered
from utils.types import RarityType


# Global state for the matching minigame (per event instance)
_matching_state = {}


def _generate_card_pairs() -> List[Tuple[Card, Card]]:
    """Generate 6 pairs of cards for the minigame.
    
    Always includes:
    - 1 Colorless card pair
    - 1 Curse pair
    - 4 random card pairs from Ironclad pool
    """
    pairs = []
    
    # Get all registered cards
    all_card_classes = list_registered('card')
    
    # Get a colorless card pair
    colorless_cards = []
    for card_idstr in all_card_classes:
        card_cls = get_registered('card', card_idstr)
        if card_cls:
            card_instance = card_cls()
            if card_instance.namespace == 'colorless':
                colorless_cards.append(card_cls)
    
    if colorless_cards:
        colorless_cls = random.choice(colorless_cards)
        pairs.append((colorless_cls(), colorless_cls()))
    
    # Get a curse pair
    curse_cards = []
    for card_idstr in all_card_classes:
        card_cls = get_registered('card', card_idstr)
        if card_cls:
            card_instance = card_cls()
            if card_instance.rarity == RarityType.CURSE:
                curse_cards.append(card_cls)
    
    if curse_cards:
        curse_cls = random.choice(curse_cards)
        pairs.append((curse_cls(), curse_cls()))
    
    # Get 4 random Ironclad card pairs (Common, Uncommon, or Rare)
    ironclad_cards = []
    for card_idstr in all_card_classes:
        card_cls = get_registered('card', card_idstr)
        if card_cls:
            card_instance = card_cls()
            if (card_instance.namespace == 'ironclad' and 
                card_instance.rarity in [RarityType.COMMON, RarityType.UNCOMMON, RarityType.RARE]):
                ironclad_cards.append(card_cls)
    
    # Weight by rarity (Common 50%, Uncommon 35%, Rare 15%)
    weighted_cards = []
    for card_cls in ironclad_cards:
        card = card_cls()
        if card.rarity == RarityType.COMMON:
            weighted_cards.extend([card_cls] * 50)
        elif card.rarity == RarityType.UNCOMMON:
            weighted_cards.extend([card_cls] * 35)
        else:  # Rare
            weighted_cards.extend([card_cls] * 15)
    
    # Select 4 unique card types for pairs
    selected_classes = set()
    while len(pairs) < 6 and weighted_cards:
        card_cls = random.choice(weighted_cards)
        if card_cls not in selected_classes:
            selected_classes.add(card_cls)
            pairs.append((card_cls(), card_cls()))
    
    return pairs


def _create_shuffled_deck(pairs: List[Tuple[Card, Card]]) -> List[dict]:
    """Create a shuffled deck of 12 cards from 6 pairs."""
    cards = []
    for pair in pairs:
        for card in pair:
            cards.append({
                'card': card,
                'idstr': card.idstr,
                'revealed': False,
                'matched': False,
            })
    random.shuffle(cards)
    return cards


@register_event(event_id='match_and_keep', acts='shared', weight=100)
class MatchAndKeep(Event):
    """Match and Keep - card matching minigame."""
    
    @classmethod
    def can_appear(cls) -> bool:
        """Can appear in any act."""
        return True
    
    def trigger(self) -> None:
        global _matching_state
        
        # Initialize minigame state
        pairs = _generate_card_pairs()
        deck = _create_shuffled_deck(pairs)
        
        _matching_state = {
            'deck': deck,
            'tries_remaining': 5,
            'matched_cards': [],
            'first_selection': None,
            'phase': 'select_first',  # 'select_first', 'select_second', 'game_over'
        }
        
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.match_and_keep.description'
        ))
        
        # Start the minigame
        actions.append(MatchAndKeepAction())
        
        self.end_event()
        add_actions(actions)


@register("action")
class MatchAndKeepAction(Action):
    """Interactive matching minigame action."""
    
    def execute(self) -> None:
        global _matching_state
        
        if not _matching_state:
            return
        
        # Check if game is over
        if _matching_state['tries_remaining'] <= 0:
            add_actions(self._end_game(), to_front=True)
            return
        
        # Check if all cards matched
        unmatched = [c for c in _matching_state['deck'] if not c['matched']]
        if not unmatched:
            add_actions(self._end_game(), to_front=True)
            return
        
        # Build selection options for face-down cards
        options = []
        for i, card_data in enumerate(_matching_state['deck']):
            if card_data['matched']:
                # Show matched card
                options.append(Option(
                    name=LocalStr(f"[MATCHED] {card_data['card'].info()}", 
                                  default=f"[MATCHED] {card_data['card'].info()}"),
                    actions=[],
                    enabled=False
                ))
            elif card_data['revealed']:
                # Show revealed but not matched
                options.append(Option(
                    name=LocalStr(f"[FACE UP] {card_data['card'].info()}",
                                  default=f"[FACE UP] {card_data['card'].info()}"),
                    actions=[],
                    enabled=False
                ))
            else:
                # Face-down card - can be selected
                options.append(Option(
                    name=LocalStr(f"Card {i+1}", default=f"Card {i+1} (Face Down)"),
                    actions=[FlipCardAction(card_index=i)]
                ))
        
        # Show tries remaining
        tries_text = f"Tries remaining: {_matching_state['tries_remaining']}"
        
        add_action(
            InputRequestAction(
                title=LocalStr(
                    'events.match_and_keep.select_card',
                    default=f"Select a card to flip. {tries_text}",
                    tries=_matching_state['tries_remaining'],
                ),
                options=options,
                max_select=1,
                must_select=True,
            ),
            to_front=True,
        )
    
    def _end_game(self) -> list:
        """End the minigame and add matched cards to deck."""
        global _matching_state
        
        actions = []
        
        # Add all matched cards to player's deck
        for card in _matching_state['matched_cards']:
            actions.append(AddCardAction(card=card, dest_pile='deck'))
        
        # Display results
        if _matching_state['matched_cards']:
            card_names = ', '.join(str(c.info()) for c in _matching_state['matched_cards'])
            actions.append(DisplayTextAction(
                text_key='events.match_and_keep.won_cards',
                default=f"You matched: {card_names}",
                cards=card_names,
            ))
        else:
            actions.append(DisplayTextAction(
                text_key='events.match_and_keep.no_matches',
                default="You didn't match any cards.",
            ))
        
        # Clear state
        _matching_state = {}
        
        return actions


@register("action")
class FlipCardAction(Action):
    """Flip a card in the matching minigame."""
    
    def __init__(self, card_index: int):
        self.card_index = card_index
    
    def execute(self) -> None:
        global _matching_state
        
        if not _matching_state:
            return
        
        deck = _matching_state['deck']
        
        if self.card_index < 0 or self.card_index >= len(deck):
            return
        
        card_data = deck[self.card_index]
        
        # Can't flip matched or already revealed cards
        if card_data['matched'] or card_data['revealed']:
            return
        
        # Flip the card
        card_data['revealed'] = True
        
        if _matching_state['first_selection'] is None:
            # First card of the pair
            _matching_state['first_selection'] = self.card_index
            # Continue selecting
            add_action(MatchAndKeepAction(), to_front=True)
            return
        else:
            # Second card - check for match
            first_index = _matching_state['first_selection']
            first_card = deck[first_index]
            
            if first_card['idstr'] == card_data['idstr']:
                # Match found!
                first_card['matched'] = True
                card_data['matched'] = True
                _matching_state['matched_cards'].append(card_data['card'])
            else:
                # No match - hide both cards after a moment
                # In a real UI, this would show both cards briefly
                # For now, we'll just reset them
                first_card['revealed'] = False
                card_data['revealed'] = False
                _matching_state['tries_remaining'] -= 1
            
            _matching_state['first_selection'] = None
            
            # Continue the game
            add_action(MatchAndKeepAction(), to_front=True)
            return


from utils.registry import list_registered
