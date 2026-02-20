"""Torch Head - Minion spawned by The Collector."""

from enemies.base import Enemy
from enemies.act2.the_collector_intentions import Tackle
from utils.types import EnemyType


class TorchHead(Enemy):
    """Torch Head is a Minion spawned by the Collector."""
    
    enemy_type = EnemyType.MINION
    
    def __init__(self):
        super().__init__(hp_range=(20, 22))
        self.add_intention(Tackle(self))
    
    def determine_next_intention(self, floor: int):
        """Torch Head always uses Tackle."""
        self.current_intention = self.intentions["Tackle"]
    
    def on_combat_start(self, floor: int):
        """Initialize combat state."""
        self.current_intention = self.intentions["Tackle"]
