from typing import Any, List, Optional, TYPE_CHECKING
from utils.registry import get_registered, list_registered
from utils.types import CardType, RarityType
import random

# Type hinting only, avoid circular import
if TYPE_CHECKING:
    from cards.base import Card
    from relics.base import Relic
    from potions.base import Potion
else:
    Card = Any  # Runtime placeholder
    Relic = Any  # Runtime placeholder
    Potion = Any  # Runtime placeholder


# todo: 对于没有指定稀有度的情况，考虑根据权重选择稀有度
def get_random_card(namespaces: Optional[List[str]] = None, 
                     rarities: Optional[List[RarityType]] = None, 
                     card_types: Optional[List[CardType]] = None, 
                     target_set: Optional[List[str]] = None, 
                     exclude_set: Optional[List[str]] = None,
                     exclude_card_ids: Optional[List[str]] = None,
                     exclude_starter: bool = False) -> Optional[Card]:
    """
    Get a random card from the registry based on criteria.
    
    args:
        namespace (Optional[List[str]]): List of namespaces to filter cards.
        rarity (Optional[List[RarityType]]): List of rarities to filter cards.
        card_type (Optional[List[CardType]]): List of card types to filter cards.
        target_set (Optional[List[str]]): List of target set to include.
        exclude_set (Optional[List[str]]): List of set to exclude.
        exclude_card_ids (Optional[List[str]]): List of card idstrs to exclude (prevents duplicates).
        exclude_starter (bool): If True, exclude STARTER rarity cards.
        
    returns:
        Optional[Card]: A random card matching the criteria, or None if none found.
    """
    
    if target_set:
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
        if exclude_card_ids and card_idstr in exclude_card_ids:
            continue
        if exclude_starter and card_instance.rarity == RarityType.STARTER:
            continue
        
        filtered_card_idstrs.append(card_idstr)
        
    if not filtered_card_idstrs:
        return None

    selected_card_idstr = random.choice(filtered_card_idstrs)
    selected_card_cls = get_registered("card", selected_card_idstr)
    return selected_card_cls() if selected_card_cls else None


# 基础概率配置（按百分比）
CARD_RARITY_PROBABILITIES = {
    "normal": {RarityType.COMMON: 60, RarityType.UNCOMMON: 37, RarityType.RARE: -2}, # 3
    "elite": {RarityType.COMMON: 50, RarityType.UNCOMMON: 40, RarityType.RARE: 5}, # 10
    "shop": {RarityType.COMMON: 54, RarityType.UNCOMMON: 37, RarityType.RARE: 4}, # 9
}

card_rarity_probabilities = CARD_RARITY_PROBABILITIES.copy()

def get_random_card_reward(namespaces: Optional[List[str]] = None,
                         encounter_type: str = "normal",
                         use_rolling_offset: bool = False,
                         exclude_set: Optional[List[str]] = None) -> Optional[Card]:
    """
    Get a random card from registry with rarity weights based on encounter type.

    args:
        namespaces (Optional[List[str]]): List of namespaces to filter cards.
        encounter_type (str): Type of encounter for rarity weights ("normal", "elite", "shop").
        use_rolling_offset (bool): If True, adjust rare chance based on common cards gained.
        exclude_set (Optional[List[str]]): List of card idstrs to exclude (prevents duplicates).

    returns:
        Optional[Card]: A random card matching criteria with weighted rarity, or None if none found.
    """
    # Get base probabilities for this encounter type
    base_probs = card_rarity_probabilities.get(encounter_type, card_rarity_probabilities["normal"]).copy()

    # Filter available cards
    all_card_idstrs = list_registered("card")
    cards_by_rarity = {
        RarityType.COMMON: [],
        RarityType.UNCOMMON: [],
        RarityType.RARE: []
    }

    for card_idstr in all_card_idstrs:
        card_cls = get_registered("card", card_idstr)
        if not card_cls:
            continue
        card_instance = card_cls()

        # Filter by namespace
        if namespaces and card_instance.namespace not in namespaces:
            continue

        # Exclude STARTER rarity cards from rewards
        if card_instance.rarity == RarityType.STARTER:
            continue

        # Exclude already selected cards (prevent duplicates)
        if exclude_set and card_idstr in exclude_set:
            continue

        # Group cards by rarity
        if card_instance.rarity in cards_by_rarity:
            cards_by_rarity[card_instance.rarity].append(card_idstr)

    # Check if any cards available for each rarity
    available_rarities = [
        (rarity, cards_by_rarity[rarity])
        for rarity in [RarityType.COMMON, RarityType.UNCOMMON, RarityType.RARE]
        if cards_by_rarity[rarity]
    ]

    if not available_rarities:
        return None
    
    # 处理负权重：将负值替换为0
    effective_probs = {}
    for rarity, _ in available_rarities:
        prob = base_probs.get(rarity, 0)
        effective_probs[rarity] = max(0, prob)  # 负权重视为0
    
    # 计算权重：基于可用的稀有度和基础概率
    total_prob = sum(effective_probs[rarity] for rarity, _ in available_rarities)
    
    # 如果总概率为0（所有权重都是0或负数），使用均匀分布
    if total_prob <= 0:
        weights = [1.0 / len(available_rarities) for _ in available_rarities]
    else:
        weights = [effective_probs[rarity] / total_prob for rarity, _ in available_rarities]

    # Randomly select rarity based on weights
    selected_rarity, card_list = random.choices(available_rarities, weights=weights, k=1)[0]
    
    # Apply rolling offset if enabled
    if use_rolling_offset:
        base_probs[RarityType.RARE] += 1
        # Decrease common chance proportionally
        base_probs[RarityType.COMMON] -= 1
    
    if selected_rarity == RarityType.RARE:
        # reset prob
        card_rarity_probabilities.clear()
        card_rarity_probabilities.update(CARD_RARITY_PROBABILITIES.copy())

    # Randomly select a card from the chosen rarity
    selected_card_idstr = random.choice(card_list)
    selected_card_cls = get_registered("card", selected_card_idstr)
    selected_card = selected_card_cls() if selected_card_cls else None

    return selected_card


def increment_card_chance_common_counter():
    """
    Increment the common card counter for rolling offset.
    Call this when a common card is taken as a reward.
    """
    from engine.game_state import game_state
    game_state.card_chance_common_counter += 1


def reset_card_chance_common_counter():
    """
    Reset the common card counter for rolling offset.
    Call this when a rare card is taken as a reward.
    """
    from engine.game_state import game_state
    game_state.card_chance_common_counter = 0


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
                      rarities: Optional[List[RarityType]] = None):
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
        
        if characters and potion_instance.category not in characters:
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
