"""Structured runtime messages for passive, post-fact reactions."""
from dataclasses import dataclass
from typing import ClassVar, Optional, TYPE_CHECKING, Any, List

if TYPE_CHECKING:
    from cards.base import Card
    from entities.creature import Creature
    from powers.base import Power


@dataclass(frozen=True)
class GameMessage:
    """Base class for emitted runtime facts."""

    uses_explicit_subscription_contracts: ClassVar[bool] = True


@dataclass(frozen=True)
class CardExhaustedMessage(GameMessage):
    """A card has already been exhausted from a pile."""

    card: "Card"
    owner: "Creature"
    source_pile: Optional[str] = None
    caused_by_card: Optional["Card"] = None


@dataclass(frozen=True)
class CardPlayedMessage(GameMessage):
    """A card's primary on-play effect has already been generated."""

    card: "Card"
    owner: "Creature"
    targets: List[Optional["Creature"]]


@dataclass(frozen=True)
class AttackPerformedMessage(GameMessage):
    """An attack action has been declared before damage resolves."""

    target: "Creature"
    source: Optional["Creature"] = None
    card: Optional["Card"] = None
    damage_type: str = "direct"


@dataclass(frozen=True)
class CardDiscardedMessage(GameMessage):
    """A card has already been discarded from a pile."""

    card: "Card"
    owner: "Creature"
    source_pile: Optional[str] = None


@dataclass(frozen=True)
class CardDrawnMessage(GameMessage):
    """A card has already been drawn into hand."""

    card: "Card"
    owner: "Creature"


@dataclass(frozen=True)
class ShuffleMessage(GameMessage):
    """The player's card piles have already been shuffled."""

    owner: "Creature"


@dataclass(frozen=True)
class CardAddedToPileMessage(GameMessage):
    """A card has already been added to a pile."""

    card: "Card"
    owner: "Creature"
    dest_pile: str
    source: Optional[str] = None
    position: Optional[Any] = None


@dataclass(frozen=True)
class PlayerTurnStartedMessage(GameMessage):
    """The player turn start boundary has been reached before normal draw."""

    owner: "Creature"
    enemies: List["Creature"]


@dataclass(frozen=True)
class PlayerTurnPostDrawMessage(GameMessage):
    """The player turn has reached the post-draw boundary."""

    owner: "Creature"
    enemies: List["Creature"]


@dataclass(frozen=True)
class PlayerTurnEndedMessage(GameMessage):
    """The player turn end boundary has already been reached."""

    owner: "Creature"
    enemies: List["Creature"]
    hand_cards: List["Card"]


@dataclass(frozen=True)
class CombatStartedMessage(GameMessage):
    """Combat setup has completed and combat-start effects may run."""

    owner: "Creature"
    enemies: List["Creature"]
    floor: int = 1


@dataclass(frozen=True)
class CombatEndedMessage(GameMessage):
    """Combat has ended and post-combat effects may run."""

    owner: "Creature"
    enemies: List["Creature"]


@dataclass(frozen=True)
class RelicObtainedMessage(GameMessage):
    """A relic has been added to the player's relic list."""

    owner: "Creature"
    relic: Any


@dataclass(frozen=True)
class ShopEnteredMessage(GameMessage):
    """The player has entered a shop room."""

    owner: "Creature"
    room: Any
    entities: Optional[List["Creature"]] = None


@dataclass(frozen=True)
class EliteVictoryMessage(GameMessage):
    """The player has won an elite combat and elite-victory relic effects may run."""

    owner: "Creature"
    room: Any
    encounter_name: str = ""
    entities: Optional[List["Creature"]] = None


@dataclass(frozen=True)
class PowerAppliedMessage(GameMessage):
    """A power has been successfully applied to a target."""

    power: "Power"
    target: "Creature"
    owner: Optional["Creature"] = None
    entities: Optional[List["Creature"]] = None


@dataclass(frozen=True)
class PotionUsedMessage(GameMessage):
    """A potion has been consumed and its primary effect has been generated."""

    potion: Any
    owner: "Creature"
    targets: List["Creature"]
    entities: Optional[List["Creature"]] = None


@dataclass(frozen=True)
class GoldGainedMessage(GameMessage):
    """Gold has already been added to the player."""

    owner: "Creature"
    amount: int


@dataclass(frozen=True)
class HealedMessage(GameMessage):
    """Healing has already been applied to a target."""

    target: "Creature"
    amount: int
    previous_hp: Optional[int] = None
    new_hp: Optional[int] = None
    source: Any = None


@dataclass(frozen=True)
class HpLostMessage(GameMessage):
    """HP loss has already been applied to a target."""

    target: "Creature"
    amount: int
    source: Any = None
    card: Optional["Card"] = None


@dataclass(frozen=True)
class DirectHpLossMessage(GameMessage):
    """Direct HP loss has already been applied to a target."""

    target: "Creature"
    amount: int
    source: Any = None
    card: Optional["Card"] = None


@dataclass(frozen=True)
class AnyHpLostMessage(GameMessage):
    """Any actual HP loss has already been applied to a target."""

    target: "Creature"
    amount: int
    source: Any = None
    card: Optional["Card"] = None


@dataclass(frozen=True)
class BlockGainedMessage(GameMessage):
    """Block has already been added to a target."""

    target: "Creature"
    amount: int
    source: Any = None
    card: Optional["Card"] = None


@dataclass(frozen=True)
class DamageDealtMessage(GameMessage):
    """Damage has already been dealt to a target."""

    target: "Creature"
    amount: int
    source: Any = None
    card: Optional["Card"] = None
    damage_type: str = "direct"


@dataclass(frozen=True)
class FatalDamageMessage(GameMessage):
    """A damage instance has already delivered a killing blow."""

    target: "Creature"
    amount: int
    source: Any = None
    card: Optional["Card"] = None
    damage_type: str = "direct"


@dataclass(frozen=True)
class PhysicalAttackTakenMessage(GameMessage):
    """A physical attack has already caused damage to a target."""

    target: "Creature"
    amount: int
    source: Any = None
    card: Optional["Card"] = None
    damage_type: str = "physical"


@dataclass(frozen=True)
class PhysicalAttackDealtMessage(GameMessage):
    """A source has already dealt physical attack damage to a target."""

    target: "Creature"
    amount: int
    source: Any = None
    card: Optional["Card"] = None
    damage_type: str = "physical"


@dataclass(frozen=True)
class StanceChangedMessage(GameMessage):
    """The player's stance has changed."""

    owner: "Creature"
    previous_status: Any
    new_status: Any


@dataclass(frozen=True)
class ScryMessage(GameMessage):
    """The player is resolving a scry effect."""

    owner: "Creature"
    count: int


@dataclass(frozen=True)
class CreatureDiedMessage(GameMessage):
    """A creature has already died."""

    creature: "Creature"
    source: Any = None
    card: Optional["Card"] = None
    damage_type: str = "direct"


EXPLICIT_SUBSCRIPTION_MESSAGE_TYPES = (
    AttackPerformedMessage,
    BlockGainedMessage,
    CardAddedToPileMessage,
    CardDiscardedMessage,
    CardDrawnMessage,
    CardExhaustedMessage,
    CardPlayedMessage,
    CombatEndedMessage,
    CombatStartedMessage,
    CreatureDiedMessage,
    DamageDealtMessage,
    FatalDamageMessage,
    DirectHpLossMessage,
    EliteVictoryMessage,
    GoldGainedMessage,
    HealedMessage,
    HpLostMessage,
    AnyHpLostMessage,
    PhysicalAttackDealtMessage,
    PhysicalAttackTakenMessage,
    PlayerTurnPostDrawMessage,
    PlayerTurnEndedMessage,
    PlayerTurnStartedMessage,
    PotionUsedMessage,
    PowerAppliedMessage,
    RelicObtainedMessage,
    ScryMessage,
    ShuffleMessage,
    ShopEnteredMessage,
    StanceChangedMessage,
)
