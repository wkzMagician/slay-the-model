"""Normal-mode relic eligibility from the fixed original canSpawn methods."""
from utils.types import CardType, RarityType

FLOOR_LIMITS = {
    "TinyChest": 35,
    "Matryoshka": 40,
    "Girya": 47,
    "PeacePipe": 47,
    "Shovel": 47,
    "AncientTeaSet": 48,
    "CeramicFish": 48,
    "TheCourier": 48,
    "DarkstonePeriapt": 48,
    "DreamCatcher": 48,
    "FrozenEgg": 48,
    "JuzuBracelet": 48,
    "MawBank": 48,
    "MealTicket": 48,
    "MeatOnBone": 48,
    "MoltenEgg": 48,
    "OldCoin": 48,
    "Omamori": 48,
    "PrayerWheel": 48,
    "QuestionCard": 48,
    "RegalPillow": 48,
    "SingingBowl": 48,
    "SmilingMask": 48,
    "ToxicEgg": 48,
    "PreservedInsect": 52,
}
CAMPFIRE_RELICS = frozenset({"Girya", "PeacePipe", "Shovel"})
SHOP_EXCLUDED = frozenset({"TheCourier", "MawBank", "OldCoin", "SmilingMask"})
BOTTLE_TYPES = {
    "BottledFlame": CardType.ATTACK,
    "BottledLightning": CardType.SKILL,
    "BottledTornado": CardType.POWER,
}


def _has_bottle_target(player, key):
    from engine.card_pools import definitions, original_id, original_rarity
    if player is None:
        return False
    records = definitions()
    for card in player.card_manager.get_pile("deck"):
        row = records.get(original_id(card))
        card_type = CardType[row.type] if row else card.card_type
        if card_type != BOTTLE_TYPES[key]:
            continue
        if key == "BottledTornado" or original_rarity(card) != RarityType.STARTER:
            return True
    return False


def eligible(relic):
    from engine.game_state import game_state
    key = relic.idstr
    limit = FLOOR_LIMITS.get(key)
    if limit is not None and game_state.current_floor > limit:
        return False
    if key in SHOP_EXCLUDED:
        from rooms.shop import ShopRoom
        if isinstance(game_state.current_room, ShopRoom):
            return False
    if key in CAMPFIRE_RELICS:
        from relics.global_relics.rare import Girya, PeacePipe, Shovel
        held = sum(isinstance(item, (Girya, PeacePipe, Shovel)) for item in game_state.player.relics)
        if held >= 2:
            return False
    if key == "Ectoplasm" and game_state.current_act > 1:
        return False
    if key in BOTTLE_TYPES:
        return _has_bottle_target(game_state.player, key)
    return True
