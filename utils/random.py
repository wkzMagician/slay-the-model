from typing import Any, List, Optional
from cards.base import Card
from potions.base import Potion
from relics.base import Relic
from utils.registry import get_registered, list_registered
from utils.types import CardType, RarityType
import random

# todo: 对于没有指定稀有度的情况，考虑根据权重选择稀有度
def get_random_card(namespaces: Optional[List[str]] = None, 
                    rarities: Optional[List[RarityType]] = None, 
                    card_types: Optional[List[CardType]] = None, 
                    target_set: Optional[List[str]] = None, 
                    exclude_set: Optional[List[str]] = None) -> Optional[Card]:
    """
    Get a random card from the registry based on criteria.
    
    args:
        namespace (Optional[List[str]]): List of namespaces to filter cards.
        rarity (Optional[List[RarityType]]): List of rarities to filter cards.
        card_type (Optional[List[CardType]]): List of card types to filter cards.
        target_set (Optional[List[str]]): List of target set to include.
        exclude_set (Optional[List[str]]): List of set to exclude.
        
    returns:
        Optional[Card]: A random card matching the criteria, or None if none found.
    """
    
    if target_set is not None:
        target_card_idstr = random.choices(target_set, k=1)[0]
        card_cls = get_registered("card", target_card_idstr)
        return card_cls() if card_cls else None
    
    all_card_idstrs = list_registered("card")
    filtered_card_idstrs = []
    for card_idstr in all_card_idstrs:
        card_cls = get_registered("card", card_idstr)
        if not card_cls:
            continue
        card_instance = card_cls()
        
        if namespaces and card_instance.namespace not in namespaces:
            continue
        if rarities and card_instance.rarity not in rarities:
            continue
        if card_types and card_instance.card_type not in card_types:
            continue
        if exclude_set and card_instance.set in exclude_set:
            continue
        
        filtered_card_idstrs.append(card_idstr)
        
    if not filtered_card_idstrs:
        return None
    
    selected_card_idstr = random.choice(filtered_card_idstrs)
    selected_card_cls = get_registered("card", selected_card_idstr)
    return selected_card_cls() if selected_card_cls else None
    

def get_random_relic(characters: Optional[List[str]] = None, 
                     rarities: Optional[List[RarityType]] = None) -> Optional[Relic]:
    """
    Get a random relic from the registry based on criteria.
    
    args:
        characters (Optional[List[str]]): List of character namespaces to filter relics.
        rarities (Optional[List[RarityType]]): List of rarities to filter relics.
        
    returns:
        Optional[Any]: A random relic matching the criteria, or None if none found.
    """
    
    # Ensure "any" namespace is included
    if characters and "any" not in characters:
        characters.append("any")
    
    all_relic_idstrs = list_registered("relic")
    filtered_relic_idstrs = []
    for relic_idstr in all_relic_idstrs:
        relic_cls = get_registered("relic", relic_idstr)
        if not relic_cls:
            continue
        relic_instance = relic_cls()
        
        if characters and relic_instance.namespace not in characters:
            continue
        if rarities and relic_instance.rarity not in rarities:
            continue
        
        # Check if relic was already obtained
        from engine.game_state import game_state
        if relic_idstr in game_state.obtained_relics:
            continue
        
        filtered_relic_idstrs.append(relic_idstr)
        
    if not filtered_relic_idstrs:
        return None
    
    selected_relic_idstr = random.choice(filtered_relic_idstrs)
    selected_relic_cls = get_registered("relic", selected_relic_idstr)
    return selected_relic_cls() if selected_relic_cls else None

def get_random_potion(characters: Optional[List[str]] = None,
                      rarities: Optional[List[RarityType]] = None) -> Optional[Potion]:
    """
    Get a random potion from registry based on criteria.
    
    args:
        characters (Optional[List[str]]): List of character namespaces to filter potions.
        rarities (Optional[List[RarityType]]): List of rarities to filter potions.
        
    returns:
        Optional[Any]: A random potion matching criteria, or None if none found.
    """
    # Ensure "any" namespace is included
    if characters and "any" not in characters:
        characters.append("any")
    
    all_potion_idstrs = list_registered("potion")
    filtered_potion_idstrs = []
    for potion_idstr in all_potion_idstrs:
        potion_cls = get_registered("potion", potion_idstr)
        if not potion_cls:
            continue
        potion_instance = potion_cls()
        
        if characters and potion_instance.namespace not in characters:
            continue
        if rarities and potion_instance.rarity not in rarities:
            continue
        
        filtered_potion_idstrs.append(potion_idstr)
        
    if not filtered_potion_idstrs:
        return None
    
    selected_potion_idstr = random.choice(filtered_potion_idstrs)
    selected_potion_cls = get_registered("potion", selected_potion_idstr)
    return selected_potion_cls() if selected_potion_cls else None


def get_random_events(floor: int = 0, count: int = 1, floors: Optional[str] = None) -> List[Any]:
    """
    Get random events from the event pool based on criteria.
    
    args:
        floor (int): Current floor number for filtering.
        count (int): Number of events to return (default: 1).
        floors (Optional[str]): Floor range filter ('early', 'mid', 'late', 'boss', 'all').
        
    returns:
        List[Any]: List of event instances matching criteria.
    """
    from events.event_pool import event_pool
    
    # Get available events based on floor
    available_metadata = event_pool.get_available_events(floor)
    
    # Filter by floor range if specified
    if floors and floors != 'all':
        floor_range = event_pool._get_floor_range(floor)
        available_metadata = [
            m for m in available_metadata
            if m.floors == floors or m.floors == 'all' or m.floors == floor_range
        ]
    
    if not available_metadata:
        return []
    
    # Get specified count of events
    if count >= len(available_metadata):
        # Return all available if count exceeds available
        selected_metadata = available_metadata
    else:
        # Random weighted selection
        selected_metadata = random.choices(
            available_metadata,
            weights=[m.weight for m in available_metadata],
            k=count
        )
    
    # Create event instances
    events = []
    for metadata in selected_metadata:
        event = metadata.event_class()
        events.append(event)
        
        # Mark unique events as used
        if metadata.is_unique:
            event_pool.mark_event_used(metadata.event_id)
    
    return events