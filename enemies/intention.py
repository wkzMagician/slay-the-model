"""Enemy intention system - defines what an enemy plans to do."""

from typing import List, TYPE_CHECKING
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from enemies.base import Enemy
    from actions.base import Action


class Intention(ABC):
    """Base class for enemy intentions.
    
    Each intention defines what an enemy plans to do and returns a list of Actions
    to execute when triggered.
    """
    
    def __init__(self, name: str, enemy: 'Enemy'):
        self.name = name
        self.enemy = enemy
    
    @abstractmethod
    def execute(self) -> List['Action']:
        """Execute this intention and return list of actions to perform.

        Returns:
            List of Action objects to queue for execution
        """
        pass
    
    def __repr__(self):
        return f"{self.__class__.__name__}(name='{self.name}')"