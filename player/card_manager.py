"""Card pile management for the player."""

from typing import List, Optional, Union, Dict, Any
from cards.base import Card
from utils.types import PilePosType

class CardManager:
    """Manages card piles and card flow for the player.

    This class is intentionally generic; higher-level logic should live in actions.
    """
    
    # todo: hand capacity is 10; if add card to hand when hand has 10 cards, move this card to discard_pile

    def __init__(self, deck: Optional[List[Card]] = None) -> None:
        # Store all piles in a single dictionary for unified management
        self.piles: Dict[str, List[Card]] = {
            'deck': list(deck or []),
            'draw_pile': [],
            'discard_pile': [],
            'hand': [],
            'exhaust_pile': [],
        }

    @property
    def deck(self) -> List[Card]:
        """Compatibility alias for older tests and call sites."""
        return self.piles['deck']

    def reset_for_combat(self) -> None:
        # Gather all cards from all piles (they belong to the player's deck)
        
        # Move all cards to draw_pile, clear other piles
        self.piles['draw_pile'] = []
        for card in self.piles['deck']:
            self.piles['draw_pile'].append(card.copy())
        self.piles['discard_pile'] = []
        self.piles['hand'] = []
        self.piles['exhaust_pile'] = []

    def shuffle_discard_to_draw(self) -> None:
        self.piles['draw_pile'].extend(self.piles['discard_pile'])
        self.piles['discard_pile'] = []
        import random
        random.shuffle(self.piles['draw_pile'])

    def draw_one(self) -> Optional[Card]:
        if not self.piles['draw_pile']:
            self.shuffle_discard_to_draw()
        if not self.piles['draw_pile']:
            return None
        card = self.piles['draw_pile'].pop()
        self.piles['hand'].append(card)
        return card

    def draw_many(self, amount: int) -> List[Card]:
        drawn = []
        for _ in range(amount):
            card = self.draw_one()
            if not card:
                break
            drawn.append(card)
        return drawn
        
    def get_card_location(self, card: Card) -> Optional[str]:
        """Get the current location of a card."""
        for pile_name, pile in self.piles.items():
            if card in pile:
                return pile_name
        return None
    
    def add_to_pile(self, card: Card, pile: str, pos: PilePosType) -> bool:
        """Add a card to a specified pile."""
        if pile not in self.piles:
            return False
        if pos == PilePosType.TOP:
            self.piles[pile].append(card)
        elif pos == PilePosType.BOTTOM:
            self.piles[pile].insert(0, card)
        elif pos == PilePosType.RANDOM:
            import random
            index = random.randint(0, len(self.piles[pile]))
            self.piles[pile].insert(index, card)
        return True
            
    def remove_from_pile(self, card: Card, pile: str) -> bool:
        """Remove a card from a specified pile.
        
        Returns:
            bool: True if the card was removed, False otherwise.
        """
        if pile in self.piles and card in self.piles[pile]:
            self.piles[pile].remove(card)
            return True
        return False

    def move_to(self, card: Card, dst: str, src: Optional[str] = None, pos: Optional[PilePosType] = None) -> bool:
        """Move a card to a specified pile.
        
        Args:
            card: The card to move (Card object)
            dst: Destination pile name ('deck', 'draw_pile', 'discard_pile', 'hand', 'exhaust_pile')
            src: Source pile name ('deck', 'draw_pile', 'discard_pile', 'hand', 'exhaust_pile')
            pos: Position to add the card in the destination pile (PilePosType)
            
        Returns:
            bool: True if the card was successfully moved, False otherwise.
        """
        if dst not in self.piles:
            return False
            
        source_pile = src if src in self.piles else self.get_card_location(card)
        if not source_pile:
            return False  # Card not found in any 
        if not pos:
            pos = PilePosType.TOP
        
        self.remove_from_pile(card, source_pile)
        return self.add_to_pile(card, dst, pos)

    def exhaust(self, card: Card, src: Optional[str]) -> bool:
        """Exhaust a card (move to exhaust pile).
        
        Args:
            card: The card to exhaust (Card object or card ID)
            src: Source pile name ('deck', 'draw_pile', 'discard_pile', 'hand')
            
        Returns:
            bool: True if the card was successfully exhausted, False otherwise.
        """
        return self.move_to(card, 'exhaust_pile', src, PilePosType.TOP)
    
    def discard(self, card: Card, src: Optional[str]) -> bool:
        """Discard a card (move to discard pile).
        
        Args:
            card: The card to discard (Card object or card ID)
            src: Source pile name ('deck', 'draw_pile', 'hand')
            
        Returns:
            bool: True if the card was successfully discarded, False otherwise.
        """
        return self.move_to(card, 'discard_pile', src, PilePosType.TOP)

    def get_pile(self, pile: str) -> List[Card]:
        """Get a pile by location name."""
        target_pile = self.piles.get(pile)
        if target_pile is None:
            raise ValueError(f"Invalid pile name: {pile}")
        return target_pile
