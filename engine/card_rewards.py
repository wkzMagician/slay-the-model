"""Combat reward protocol: integer rarity, duplicate rejection, then previews."""
from typing import cast
from engine.card_pools import current_pools, definitions, original_rarity, java_id_key
from engine.random_streams import get_rng, StreamRandom
from utils.types import CardType, RarityType

MAX_DUPLICATE_ATTEMPTS = 10000


def roll_rarity(rng, encounter_type="normal", *, use_offset=True):
    from engine.game_state import game_state
    rare, uncommon = {"normal": (3, 37), "elite": (10, 40), "shop": (9, 37)}.get(encounter_type, (3, 37))
    if any(getattr(relic, "idstr", None) == "NlothGift" for relic in game_state.player.relics) and encounter_type != "shop":
        rare *= 3
    roll = rng.random_int(99) + (game_state.card_rarity_offset if use_offset else 0)
    return RarityType.RARE if roll < rare else RarityType.UNCOMMON if roll < rare + uncommon else RarityType.COMMON


def update_compensation(rarity):
    from engine.game_state import game_state
    if rarity == RarityType.COMMON:
        game_state.card_rarity_offset = max(-40, game_state.card_rarity_offset - 1)
    elif rarity == RarityType.RARE:
        game_state.card_rarity_offset = 5


def upgrade_chance(act, ascension):
    return (0.0, 0.25, 0.5)[max(1, min(3, act)) - 1] / (2 if ascension >= 12 else 1)


def reward_cards(total=3, namespaces=None, encounter_type="normal", use_rolling_offset=True,
                 exclude_set=None, allow_upgraded=True, *, preview_pile=None):
    from engine.game_state import game_state
    rng = cast(StreamRandom, get_rng("card"))
    pools = current_pools()
    records = definitions()
    # None is the Prismatic Shard/all-color library route. Its original helper
    # shuffles the full rarity list, then sorts by cardID before selecting.
    any_color = namespaces is None
    by_tier = {}
    for rarity in (RarityType.COMMON, RarityType.UNCOMMON, RarityType.RARE):
        by_tier[rarity] = pools.candidates(namespaces, [rarity],
                                         [CardType.ATTACK, CardType.SKILL, CardType.POWER],
                                         pool_kind="library" if any_color else "current")
    if not any(by_tier.values()):
        return []
    blocked = set(exclude_set or [])
    blocked.update(row.id for row in records.values() if row.project_id in blocked)
    chosen = []
    for _ in range(total):
        rarity = roll_rarity(rng, encounter_type, use_offset=use_rolling_offset)
        if use_rolling_offset and encounter_type != "shop":
            update_compensation(rarity)
        candidates = by_tier[rarity]
        # Explicit unsupported/depleted-pool boundary: no fallback tier or
        # synthetic result. Normal unlocked reward pools contain enough IDs.
        if not any(card_id not in blocked for card_id in candidates):
            continue
        for _attempt in range(MAX_DUPLICATE_ATTEMPTS):
            if any_color:
                shuffled = list(reversed(candidates))
                rng.shuffle(shuffled)
                sample = sorted(shuffled, key=java_id_key)
            else:
                sample = candidates
            card_id = rng.choice(sample)
            if card_id not in blocked:
                blocked.add(card_id)
                chosen.append(records[card_id].make_card())
                break
        else:
            raise RuntimeError("Card reward duplicate rejection exceeded its safety limit")
    # Copy only after every candidate has been selected. Never upgrade a pool
    # prototype, or interleave upgrade RNG with the next candidate's rarity.
    result = [card.copy() for card in chosen]
    chance = upgrade_chance(game_state.current_act, game_state.ascension)
    for card in result:
        if (allow_upgraded and original_rarity(card) != RarityType.RARE
                and rng.random_boolean(chance) and card.can_upgrade()):
            card.upgrade()
            continue
        if preview_pile == "deck":
            for relic in list(game_state.player.relics):
                hook = getattr(relic, "should_upgrade_added_card", None)
                if hook and hook(card, preview_pile) and card.can_upgrade():
                    card.upgrade()
    return result
