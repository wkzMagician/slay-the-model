"""Card pile management for the player."""

from typing import List, Optional, TypeVar, Union, Dict

# Define a Card type - this can be a string (card ID) or a Card object
Card = TypeVar('Card')
CardID = str

class CardManager:
    """Manages card piles and card flow for the player.

    This class is intentionally generic; higher-level logic should live in actions.
    """

    def __init__(self, deck: Optional[List[Union[Card, CardID]]] = None) -> None:
        # Store all piles in a single dictionary for unified management
        self.piles: Dict[str, List[Union[Card, CardID]]] = {
            'deck': list(deck or []),
            'draw_pile': [],
            'discard_pile': [],
            'hand': [],
            'exhaust_pile': [],
        }

    # Property accessors for backward compatibility
    @property
    def deck(self) -> List[Union[Card, CardID]]:
        return self.piles['deck']

    @property
    def draw_pile(self) -> List[Union[Card, CardID]]:
        return self.piles['draw_pile']

    @property
    def discard_pile(self) -> List[Union[Card, CardID]]:
        return self.piles['discard_pile']

    @property
    def hand(self) -> List[Union[Card, CardID]]:
        return self.piles['hand']

    @property
    def exhaust_pile(self) -> List[Union[Card, CardID]]:
        return self.piles['exhaust_pile']

    def reset_for_combat(self) -> None:
        self.piles['draw_pile'] = list(self.piles['deck'])
        self.piles['discard_pile'] = []
        self.piles['hand'] = []
        self.piles['exhaust_pile'] = []

    def shuffle_discard_to_draw(self) -> None:
        self.piles['draw_pile'].extend(self.piles['discard_pile'])
        self.piles['discard_pile'] = []
        import random
        random.shuffle(self.piles['draw_pile'])

    def draw_one(self) -> Optional[Union[Card, CardID]]:
        if not self.piles['draw_pile']:
            self.shuffle_discard_to_draw()
        if not self.piles['draw_pile']:
            return None
        card = self.piles['draw_pile'].pop()
        self.piles['hand'].append(card)
        return card

    def draw_many(self, amount: int) -> List[Union[Card, CardID]]:
        drawn = []
        for _ in range(amount):
            card = self.draw_one()
            if not card:
                break
            drawn.append(card)
        return drawn

    def discard_from_hand(self, card: Union[Card, CardID]) -> None:
        """Discard a card from hand to discard pile."""
        self.move_to(card, 'discard_pile', 'hand')

    def move_to(self, card: Union[Card, CardID], pile: str, source_pile: Optional[str] = None) -> bool:
        """Move a card to a specified pile.
        
        Args:
            card: The card to move (Card object or card ID)
            pile: Destination pile name ('deck', 'draw_pile', 'discard_pile', 'hand', 'exhaust_pile')
            source_pile: Optional source pile name. If provided, removes card from source pile first.
            
        Returns:
            bool: True if the card was successfully moved, False otherwise.
        """
        if pile not in self.piles:
            return False
            
        # Remove from source pile if specified
        if source_pile and source_pile in self.piles:
            source_list = self.piles[source_pile]
            if card in source_list:
                source_list.remove(card)
        
        # Add to destination pile
        self.piles[pile].append(card)
        return True

    def exhaust(self, card: Union[Card, CardID], source_pile: Optional[str] = None) -> bool:
        """Exhaust a card (move to exhaust pile).
        
        Args:
            card: The card to exhaust (Card object or card ID)
            source_pile: Optional source pile name. If not provided, will search all piles.
            
        Returns:
            bool: True if the card was successfully exhausted, False otherwise.
        """
        if source_pile:
            # Move from specified source pile
            return self.move_to(card, 'exhaust_pile', source_pile)
        else:
            # Search all piles for the card
            for pile_name in ['hand', 'draw_pile', 'discard_pile', 'deck']:
                if pile_name in self.piles and card in self.piles[pile_name]:
                    # Found the card, move it to exhaust pile
                    self.piles[pile_name].remove(card)
                    self.piles['exhaust_pile'].append(card)
                    return True
            return False

    def move_to_discard(self, card: Union[Card, CardID]) -> None:
        """Move a card to discard pile (without removing from source)."""
        self.move_to(card, 'discard_pile')

    def move_to_draw_top(self, card: Union[Card, CardID]) -> None:
        """Move a card to draw pile top (without removing from source)."""
        self.move_to(card, 'draw_pile')

    def add_to_deck(self, card: Union[Card, CardID]) -> None:
        """Add a card to the deck."""
        self.piles['deck'].append(card)

    def remove_from_deck(self, card: Union[Card, CardID]) -> bool:
        """Remove a card from the deck."""
        if card in self.piles['deck']:
            self.piles['deck'].remove(card)
            return True
        return False

    def get_pile(self, location: str) -> Optional[List[Union[Card, CardID]]]:
        """Get a pile by location name."""
        return self.piles.get(location)

    def obtain(self, total: int, card_type: str, rarity: str, location: str = "deck") -> None:
        """Obtain cards into the specified pile. Selection logic belongs to actions/UI."""
        if total <= 0:
            return
        # Placeholder for higher-level logic. Here we just append card identifiers if provided.
        # Actions can decide which card IDs to pass in.
        return None

    def remove(self, count: int, location: str = "deck") -> None:
        """Remove cards from a pile. Actual selection should be handled by actions/UI."""
        if count <= 0:
            return
        pile = self.get_pile(location)
        if not pile:
            return
        # Higher-level logic should handle which cards to remove
        return None

    def transform(self, count: int, location: str = "deck") -> None:
        """Transform cards in a pile. Selection logic belongs to actions/UI."""
        if count <= 0:
            return
        pile = self.get_pile(location)
        if not pile:
            return
        # Higher-level logic should handle which cards to transform
        return None

    def upgrade(self, count: int, location: str = "deck") -> None:
        """Upgrade cards in a pile. Selection logic belongs to actions/UI."""
        if count <= 0:
            return
        pile = self.get_pile(location)
        if not pile:
            return
        # Higher-level logic should handle which cards to upgrade
        return None
