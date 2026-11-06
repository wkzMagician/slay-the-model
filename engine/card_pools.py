"""Run-owned normal-mode card pools, independent of Python import order.

The fixed source/JDK catalog supplies IDs, pool metadata and library iteration.
Card effects still belong to the existing Python definitions. Locked profiles
and deferred special modes have separate implementation/acceptance scopes.
"""
from dataclasses import dataclass
from functools import lru_cache
import importlib
import json
from pathlib import Path

from utils.types import CardType, RarityType

COLORS = ("ironclad", "silent", "defect", "watcher")
NAMESPACES = (*COLORS, "colorless", "curse", "status")
TIERS = ("COMMON", "UNCOMMON", "RARE")


@dataclass(frozen=True)
class CardDefinition:
    id: str
    namespace: str
    rarity: str
    type: str
    module: str | None
    cls: str | None
    healing: bool

    @property
    def project_id(self) -> str | None:
        return f"{self.module.split('.')[1]}.{self.cls}" if self.module else None

    def make_card(self):
        if self.module is None or self.cls is None:
            raise ValueError(f"No normal-mode Python definition for {self.id}")
        card = getattr(importlib.import_module(self.module), self.cls)()
        # Keep pool identity/rarity distinct from independently audited class
        # metadata; do not silently rewrite the card definition or its effects.
        card._original_card_id = self.id
        return card


@lru_cache(maxsize=1)
def catalog() -> tuple[CardDefinition, ...]:
    data = json.loads(Path(__file__).with_name("original_cards.json").read_text(encoding="utf-8"))
    return tuple(CardDefinition(**row) for row in data["cards"])


@lru_cache(maxsize=1)
def definitions() -> dict[str, CardDefinition]:
    return {row.id: row for row in catalog()}


def original_id(card) -> str:
    value = getattr(card, "_original_card_id", None)
    if isinstance(value, str):
        return value
    project_id = getattr(card, "idstr", None)
    return next((row.id for row in catalog() if row.project_id == project_id), str(project_id))


def original_rarity(card) -> RarityType:
    row = definitions().get(original_id(card))
    if row is None:
        return card.rarity
    return RarityType["STARTER" if row.rarity == "BASIC" else row.rarity]


def java_id_key(value: str) -> bytes:
    return value.encode("utf-16-be", errors="surrogatepass")


class CardPools:
    def __init__(self):
        self.current: dict[tuple[str, str | None], list[str]] = {
            (color, tier): [row.id for row in catalog() if row.namespace == color and row.rarity == tier]
            for color in COLORS for tier in TIERS
        }
        self.current[("colorless", None)] = [row.id for row in catalog() if row.namespace == "colorless"
                                            and row.rarity not in ("BASIC", "SPECIAL") and row.type != "STATUS"]
        excluded = {"Necronomicurse", "AscendersBane", "CurseOfTheBell", "Pride"}
        self.current[("curse", None)] = [row.id for row in catalog() if row.namespace == "curse" and row.id not in excluded]
        self.source = {key: list(reversed(values)) for key, values in self.current.items()}

    def candidates(self, namespaces=None, rarities=None, card_types=None, *, pool_kind="library", exclude_starter=False):
        if pool_kind not in {"library", "current", "source", "combat", "transform", "shop"}:
            raise ValueError(f"Unknown card pool protocol: {pool_kind}")
        if pool_kind == "library":
            ids = [row.id for row in catalog() if row.module is not None]
        else:
            if namespaces is None:
                if pool_kind == "shop":
                    namespaces = (*COLORS, "colorless")
                else:
                    from engine.game_state import game_state
                    namespaces = [game_state.player.namespace]
            ids = []
            for color in namespaces:
                keys = [(color, tier) for tier in TIERS] if color in COLORS else [(color, None)]
                for key in keys:
                    source = pool_kind in ("source", "combat") or pool_kind == "transform" and key[1] != "COMMON"
                    ids.extend((self.source if source else self.current).get(key, []))
        records = definitions()
        result = []
        for card_id in ids:
            row = records[card_id]
            if namespaces and pool_kind == "library":
                project_namespace = row.module.split(".")[1] if row.module else row.namespace
                if row.namespace not in namespaces and project_namespace not in namespaces:
                    continue
            rarity = RarityType["STARTER" if row.rarity == "BASIC" else row.rarity]
            if rarities and rarity not in rarities:
                continue
            if card_types and CardType[row.type] not in card_types:
                continue
            if exclude_starter and row.rarity == "BASIC":
                continue
            if pool_kind == "combat" and row.healing:
                continue
            result.append(card_id)
        if pool_kind == "shop":
            result.sort(key=java_id_key)
        return result


def current_pools() -> CardPools:
    from engine.game_state import game_state
    pools = getattr(game_state, "card_pools", None)
    if not isinstance(pools, CardPools):
        pools = CardPools()
        game_state.card_pools = pools
    return pools
