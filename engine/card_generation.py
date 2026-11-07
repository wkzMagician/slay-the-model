"""Original selection protocols for special menus and permanent transforms."""
from typing import cast

from engine.card_pools import (
    CURSE_TRANSFORM_IDS, NAMESPACES, current_pools, definitions, java_id_key, original_id,
)
from engine.card_rewards import MAX_DUPLICATE_ATTEMPTS, roll_rarity
from engine.random_streams import StreamRandom, get_rng
from utils.types import CardType, RarityType


def _pick_distinct(ids, seen, rng):
    if not any(card_id not in seen for card_id in ids):
        return None
    for _ in range(MAX_DUPLICATE_ATTEMPTS):
        card_id = rng.choice(ids)
        if card_id not in seen:
            return card_id
    raise RuntimeError("Card selection duplicate rejection exceeded its safety limit")


def fixed_choices(total, namespaces, rarities, card_types, pool_kind, rng):
    if namespaces and any(namespace not in NAMESPACES for namespace in namespaces):
        from utils.random import get_random_card
        result = []
        selected = []
        for _ in range(total):
            card = get_random_card(
                namespaces=namespaces, rarities=rarities, card_types=card_types,
                exclude_card_ids=selected, exclude_starter=True, rng=rng,
            )
            if card is not None:
                selected.append(card.idstr)
                result.append(card)
        return result
    ids = current_pools().candidates(
        namespaces, rarities, card_types, pool_kind=pool_kind, exclude_starter=True,
    )
    seen = set()
    result = []
    for _ in range(min(total, len(set(ids)))):
        card_id = _pick_distinct(ids, seen, rng)
        if card_id is None:
            break
        seen.add(card_id)
        result.append(definitions()[card_id].make_card())
    return result


def neow_choices(total, namespace, rare_only=False):
    if namespace is None:
        from engine.game_state import game_state
        namespace = game_state.player.namespace
    colorless = namespace == "colorless"
    rarity_rng = cast(StreamRandom, get_rng("neow"))
    card_rng = get_rng("card") if colorless else rarity_rng
    seen = set()
    result = []
    for _ in range(total):
        rarity = RarityType.UNCOMMON if rarity_rng.random_boolean(0.33) else RarityType.COMMON
        if rare_only:
            rarity = RarityType.RARE
        elif colorless and rarity == RarityType.COMMON:
            rarity = RarityType.UNCOMMON
        ids = current_pools().candidates(
            [namespace], [rarity], pool_kind="sorted" if colorless else "current",
        )
        card_id = _pick_distinct(ids, seen, card_rng)
        if card_id is not None:
            seen.add(card_id)
            result.append(definitions()[card_id].make_card())
    return result


def foreign_choices(total=3):
    rarity_rng = cast(StreamRandom, get_rng("card_random"))
    card_rng = get_rng("card")
    records = definitions()
    by_tier = {}
    for rarity in (RarityType.COMMON, RarityType.UNCOMMON, RarityType.RARE):
        ids = current_pools().candidates(
            rarities=[rarity], card_types=[CardType.ATTACK], pool_kind="library",
        )
        by_tier[rarity] = [card_id for card_id in ids if not records[card_id].healing]
    available = set().union(*by_tier.values())
    seen = set()
    result = []
    for _ in range(min(total, len(available))):
        for _attempt in range(MAX_DUPLICATE_ATTEMPTS):
            roll = rarity_rng.random_int(99)
            rarity = RarityType.COMMON if roll < 55 else RarityType.UNCOMMON if roll < 85 else RarityType.RARE
            ids = list(reversed(by_tier[rarity]))
            if not ids:
                continue
            rarity_rng.shuffle(ids)
            card_id = card_rng.choice(sorted(ids, key=java_id_key))
            if card_id not in seen:
                seen.add(card_id)
                result.append(records[card_id].make_card())
                break
        else:
            raise RuntimeError("Foreign Influence duplicate rejection exceeded its safety limit")
    return result


def library_choices(total=20):
    from engine.game_state import game_state
    rng = get_rng("card")
    pools = current_pools()
    namespace = game_state.player.namespace
    by_tier = {
        rarity: pools.candidates([namespace], [rarity], pool_kind="current")
        for rarity in (RarityType.COMMON, RarityType.UNCOMMON, RarityType.RARE)
    }
    available = set().union(*by_tier.values())
    seen = set()
    result = []
    for _ in range(min(total, len(available))):
        for _attempt in range(MAX_DUPLICATE_ATTEMPTS):
            rarity = roll_rarity(rng)
            ids = by_tier[rarity]
            if not ids:
                continue
            card_id = rng.choice(ids)
            if card_id not in seen:
                seen.add(card_id)
                card = definitions()[card_id].make_card()
                for relic in list(game_state.player.relics):
                    hook = getattr(relic, "should_upgrade_added_card", None)
                    if hook and hook(card, "deck") and card.can_upgrade():
                        card.upgrade()
                result.append(card)
                break
        else:
            raise RuntimeError("Library duplicate rejection exceeded its safety limit")
    # The original grid group inserts each accepted card at the bottom (index 0).
    return list(reversed(result))


def transformed_card(card, rng):
    from engine.game_state import game_state
    pools = current_pools()
    card_id = original_id(card)
    record = definitions().get(card_id)
    namespace = record.namespace if record else card.namespace
    is_curse = namespace == "curse" or card.card_type == CardType.CURSE
    if is_curse:
        ids = list(CURSE_TRANSFORM_IDS)
    elif namespace == "colorless":
        ids = list(pools.source[("colorless", None)])
    else:
        ids = pools.candidates([game_state.player.namespace], pool_kind="transform")
    ids = [value for value in ids if value != card_id]
    if not ids:
        return None
    if is_curse:
        selected = ids[rng.random_int(0, len(ids) - 1)]
    else:
        selected = rng.choice(ids)
    return definitions()[selected].make_card()
