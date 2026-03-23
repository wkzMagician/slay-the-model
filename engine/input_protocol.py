from dataclasses import dataclass, field
from typing import Dict, List, TYPE_CHECKING

from utils.option import Option

if TYPE_CHECKING:
    from actions.base import Action


@dataclass
class InputRequest:
    """Declarative description of a user or AI decision point."""

    title: object = None
    options: List[Option] = field(default_factory=list)
    max_select: int = 1
    must_select: bool = True
    context: Dict = field(default_factory=dict)
    request_type: str = "selection"
    allow_menu: bool = True


@dataclass
class InputSubmission:
    """Concrete action payload produced after resolving an InputRequest."""

    actions: List["Action"] = field(default_factory=list)
