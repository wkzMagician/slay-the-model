from engine.random_streams import get_rng, StreamRandom
from typing import Any, List, Optional, TYPE_CHECKING, cast
from utils.registry import get_registered, list_registered
from utils.types import CardType, RarityType

# Type hinting only, avoid circular import
if TYPE_CHECKING:
    from cards.base import Card
    from relics.base import Relic
    from potions.base import Potion
else:
    Card = Any  # Runtime placeholder
    Relic = Any  # Runtime placeholder
    Potion = Any  # Runtime placeholder


def _get_registry_card(namespaces: Optional[List[str]] = None,
                     rarities: Optional[List[RarityType]] = None, 
                     card_types: Optional[List[CardType]] = None, 
                     target_set: Optional[List[str]] = None, 
                     exclude_set: Optional[List[str]] = None,
                     exclude_card_ids: Optional[List[str]] = None,
                     exclude_starter: bool = False, rng=None) -> Optional[Card]:
    """
    Get a random card from the registry based on criteria.
    
    args:
        namespace (Optional[List[str]]): List of namespaces to filter cards.
        rarity (Optional[List[RarityType]]): List of rarities to filter cards.
        card_type (Optional[List[CardType]]): List of card types to filter cards.
        target_set (Optional[List[str]]): List of target set to include.
        exclude_set (Optional[List[str]]): List of set to exclude.
        exclude_card_ids (Optional[List[str]]): Card.idstr values to exclude (prevents duplicates).
        exclude_starter (bool): If True, exclude STARTER rarity cards.
        
    returns:
        Optional[Card]: A random card matching the criteria, or None if none found.
    """
    
    rng = rng if rng is not None else get_rng("card_random")
    if target_set:
        target_card_idstr = rng.choices(target_set, k=1)[0]
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
        if exclude_card_ids and card_instance.idstr in exclude_card_ids:
            continue
        if exclude_starter and card_instance.rarity == RarityType.STARTER:
            continue
        
        filtered_card_idstrs.append(card_idstr)
        
    if not filtered_card_idstrs:
        return None

    selected_card_idstr = rng.choice(filtered_card_idstrs)
    selected_card_cls = get_registered("card", selected_card_idstr)
    return selected_card_cls() if selected_card_cls else None


def get_random_card(namespaces=None, rarities=None, card_types=None, target_set=None,
                    exclude_set=None, exclude_card_ids=None, exclude_starter=False, rng=None,
                    *, pool_kind="library"):
    from engine.card_pools import current_pools, definitions, NAMESPACES
    rng = rng if rng is not None else get_rng("card_random")
    # Explicit extension/target-set API retains its registration-based meaning.
    # Normal four-character consumers use the fixed original catalog.
    if target_set or namespaces and any(name not in NAMESPACES for name in namespaces):
        return _get_registry_card(namespaces, rarities, card_types, target_set,
                                  exclude_set, exclude_card_ids, exclude_starter, rng)
    records = definitions()
    ids = current_pools().candidates(namespaces, rarities, card_types,
                                    pool_kind=pool_kind, exclude_starter=exclude_starter)
    blocked = set(exclude_card_ids or [])
    ids = [value for value in ids if value not in blocked and records[value].project_id not in blocked]
    if exclude_set:
        ids = [value for value in ids if getattr(records[value].make_card(), "set", None) not in exclude_set]
    return records[rng.choice(ids)].make_card() if ids else None


# 基础概率配置（按百分比）
CARD_RARITY_PROBABILITIES = {
    "normal": {RarityType.COMMON: 60, RarityType.UNCOMMON: 37, RarityType.RARE: 3},
    "elite": {RarityType.COMMON: 50, RarityType.UNCOMMON: 40, RarityType.RARE: 10},
    "shop": {RarityType.COMMON: 54, RarityType.UNCOMMON: 37, RarityType.RARE: 9},
}

card_rarity_probabilities = CARD_RARITY_PROBABILITIES.copy()

def get_card_reward_options(total=3, namespaces=None, encounter_type="normal", use_rolling_offset=True,
                            exclude_set=None, allow_upgraded=True, *, preview_pile=None):
    from engine.card_rewards import reward_cards
    return reward_cards(total, namespaces, encounter_type, use_rolling_offset,
                        exclude_set, allow_upgraded, preview_pile=preview_pile)


def get_random_card_reward(namespaces=None, encounter_type="normal", use_rolling_offset=False,
                           exclude_set=None, allow_upgraded=False):
    """Single-slot compatibility API; menus must generate the whole batch first."""
    cards = get_card_reward_options(1, namespaces, encounter_type, use_rolling_offset,
                                    exclude_set, allow_upgraded)
    return cards[0] if cards else None


def _get_card_reward_upgrade_chance(act: int, ascension: int) -> float:
    """Get upgraded card chance for combat rewards by act and ascension."""
    base_chance_by_act = {
        1: 0.0,
        2: 0.25,
        3: 0.5,
    }
    normalized_act = max(1, min(3, act))
    chance = base_chance_by_act[normalized_act]
    if ascension >= 12:
        chance /= 2
    return chance


def increment_card_chance_common_counter():
    """Compatibility API: account for a generated COMMON candidate, not a claim."""
    from engine.card_rewards import update_compensation
    update_compensation(RarityType.COMMON)


def reset_card_chance_common_counter():
    """Compatibility API: reset after generating a RARE candidate."""
    from engine.card_rewards import update_compensation
    update_compensation(RarityType.RARE)


def _get_registry_relic(characters: Optional[List[str]] = None,
                     rarities: Optional[List[RarityType]] = None,
                     exclude: Optional[List[str]] = None) -> Optional[Relic]:
    """
    Get a random relic from the registry based on criteria.
    
    args:
        characters (Optional[List[str]]): List of character namespaces to filter relics.
        rarities (Optional[List[RarityType]]): List of rarities to filter relics.
        exclude (Optional[List[str]]): List of relic idstrs to exclude.
        
    returns:
        Optional[Any]: A random relic matching the criteria, or None if none found.
    """
    
    from engine.game_state import game_state

    if rarities and set(rarities) == {RarityType.BOSS}:
        return game_state.boss_relic_pool.draw(exclude=exclude or (), characters=characters)

    normalized_characters: Optional[set[str]] = None
    if characters:
        normalized_characters = {str(character).lower() for character in characters}
    else:
        player = getattr(game_state, "player", None)
        namespace = getattr(player, "namespace", None)
        if namespace:
            normalized_characters = {str(namespace).lower()}
    if normalized_characters is not None:
        normalized_characters.update({"any", "global"})
    
    all_relic_idstrs = list_registered("relic")
    filtered_relic_idstrs = []
    for relic_idstr in all_relic_idstrs:
        relic_cls = get_registered("relic", relic_idstr)
        if not relic_cls:
            continue
        relic_instance = relic_cls()
        
        if normalized_characters and str(relic_instance.namespace).lower() not in normalized_characters:
            continue
        if rarities and relic_instance.rarity not in rarities:
            continue
        
        # Check if relic is excluded
        if exclude and relic_idstr in exclude:
            continue

        can_spawn = getattr(relic_instance, "can_spawn", None)
        if callable(can_spawn) and not can_spawn():
            continue
        can_spawn_legacy = getattr(relic_instance, "canSpawn", None)
        if callable(can_spawn_legacy) and not can_spawn_legacy():
            continue
        
        # Check if relic was already obtained
        if relic_idstr in game_state.obtained_relics:
            continue
        
        filtered_relic_idstrs.append(relic_idstr)
        
    if not filtered_relic_idstrs:
        return None
    
    selected_relic_idstr = get_rng("relic").choice(filtered_relic_idstrs)
    selected_relic_cls = get_registered("relic", selected_relic_idstr)
    return selected_relic_cls() if selected_relic_cls else None

def _get_registry_potion(characters: Optional[List[str]] = None,
                      rarities: Optional[List[RarityType]] = None):
    """
    Get a random potion from registry based on criteria.
    
    args:
        characters (Optional[List[str]]): List of character namespaces to filter potions.
        rarities (Optional[List[RarityType]]): List of rarities to filter potions.
        
    returns:
        Optional[Any]: A random potion matching criteria, or None if none found.
    """
    import potions  # Ensure potion classes are registered before querying the registry.

    from engine.game_state import game_state

    normalized_characters = None
    if characters:
        normalized_characters = {str(character).lower() for character in characters}
        normalized_characters.update({"any", "global"})
    else:
        player = getattr(game_state, "player", None)
        character = getattr(player, "character", None)
        namespace = getattr(player, "namespace", None)
        tokens = {
            str(value).lower()
            for value in (character, namespace)
            if value
        }
        if tokens:
            normalized_characters = tokens
            normalized_characters.update({"any", "global"})

    all_potion_idstrs = list_registered("potion")
    filtered_potion_idstrs = []
    for potion_idstr in all_potion_idstrs:
        potion_cls = get_registered("potion", potion_idstr)
        if not potion_cls:
            continue
        potion_instance = potion_cls()
        category = str(getattr(potion_instance, "category", "")).lower()

        if normalized_characters and category not in normalized_characters:
            continue
        if rarities and potion_instance.rarity not in rarities:
            continue

        filtered_potion_idstrs.append(potion_idstr)

    if not filtered_potion_idstrs:
        return None

    if not rarities:
        rarity_roll = get_rng("potion").random()
        if rarity_roll < 0.65:
            rolled_rarity = RarityType.COMMON
        elif rarity_roll < 0.90:
            rolled_rarity = RarityType.UNCOMMON
        else:
            rolled_rarity = RarityType.RARE
        rarity_filtered = []
        for potion_idstr in filtered_potion_idstrs:
            potion_cls = get_registered("potion", potion_idstr)
            if potion_cls is None:
                continue
            if potion_cls().rarity == rolled_rarity:
                rarity_filtered.append(potion_idstr)
        if rarity_filtered:
            filtered_potion_idstrs = rarity_filtered

    selected_potion_idstr = get_rng("potion").choice(filtered_potion_idstrs)
    selected_potion_cls = get_registered("potion", selected_potion_idstr)
    return selected_potion_cls() if selected_potion_cls else None


def get_random_relic(characters=None, rarities=None, exclude=None, *, from_end=False):
    from engine.game_state import game_state
    from relics.pools import TIERS
    tiers = list(rarities or [RarityType.COMMON, RarityType.UNCOMMON, RarityType.RARE])
    requested = {value.lower() for value in characters} if characters else {game_state.player.namespace}
    if requested != {game_state.player.namespace} or any(tier.name not in TIERS for tier in tiers):
        return _get_registry_relic(characters, rarities, exclude)
    rng = cast(StreamRandom, get_rng("relic"))
    if set(tiers) == {RarityType.COMMON, RarityType.UNCOMMON, RarityType.RARE}:
        roll = rng.random_int(0, 99)
        tier = RarityType.COMMON if roll < 50 else RarityType.UNCOMMON if roll < 83 else RarityType.RARE
    else:
        tier = tiers[0] if len(tiers) == 1 else rng.choice(tiers)
    if tier == RarityType.BOSS:
        return game_state.boss_relic_pool.draw(exclude=exclude or (), characters=characters)
    return game_state.relic_pools.draw(tier, exclude or (), characters, from_end=from_end)


def get_random_potion(characters=None, rarities=None, *, uniform=False, limited=False):
    from engine.game_state import game_state
    from potions.pool import catalog, draw_potion
    roles = {value.lower() for value in characters} if characters else {game_state.player.namespace}
    if len(roles) != 1 or not roles.issubset(catalog()["pools"]):
        return _get_registry_potion(characters, rarities)
    return draw_potion(next(iter(roles)), rarities, uniform=uniform, limited=limited)


def get_random_events(act: int = 1, count: int = 1) -> List[Any]:
    """
    Get random events from the event pool based on current Act.
    
    args:
        act (int): Current Act number (1-3) for filtering.
        count (int): Number of events to return (default: 1).
        
    returns:
        List[Any]: List of event instances matching criteria.
    """
    from events.event_pool import event_pool
    
    events = []
    for _ in range(max(0, count)):
        metadata = event_pool.draw_metadata(act)
        if metadata is None:
            break
        events.append(metadata.event_class())
    return events
