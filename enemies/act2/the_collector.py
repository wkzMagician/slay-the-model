"""The Collector - Act 2 Elite enemy."""

import random
from typing import List

from enemies.act2.the_collector_intentions import Buff, Fireball, MegaDebuff, Spawn
from enemies.base import Enemy
from utils.types import EnemyType


class TorchHead(Enemy):
    """Minion spawned by The Collector.
    
    Simple enemy that only uses Tackle.
    This is a summoned minion and should not trigger on_fatal effects.
    """
    
    enemy_type = EnemyType.NORMAL
    
    def __init__(self):
        super().__init__(hp_range=(38, 40), is_minion=True) # todo: 40-45 a7
        
        # Register intentions
        from enemies.act2.the_collector_intentions import Tackle
        self.add_intention(Tackle(self))
    
    def determine_next_intention(self, floor: int) -> None:
        """Torch Head only has one attack."""
        self.current_intention = self.intentions["Tackle"]


class TheCollector(Enemy):
    """Elite enemy found in Act 2.
    
    Summons Torch Head minions and buffs them.
    Always starts with Spawn.
    Always uses Mega Debuff on turn 4.
    Cannot use Buff twice in a row.
    Cannot use Fireball 3 times in a row.
    """
    
    enemy_type = EnemyType.ELITE
    
    def __init__(self):
        super().__init__(hp_range=(282, 282)) # todo: 300 a9
        self._turn_count = 0
        self._used_mega_debuff = False
        
        # Register intentions
        self.add_intention(Spawn(self))
        self.add_intention(Fireball(self))
        self.add_intention(Buff(self))
        self.add_intention(MegaDebuff(self))
    
    def on_combat_start(self, floor: int) -> None:
        """Initialize combat state."""
        super().on_combat_start(floor)
        self._turn_count = 0
    
    def _count_torch_heads(self) -> int:
        """Count alive Torch Heads in battle."""
        from engine.game_state import game_state
        enemies = (
            game_state.current_combat.enemies
            if game_state.current_combat is not None
            else []
        )

        count = 0
        for enemy in enemies:
            if enemy.is_alive and isinstance(enemy, TorchHead):
                count += 1
        return count
    
    def determine_next_intention(self, floor: int) -> None:
        """Determine next intention based on pattern."""
        self._turn_count += 1
        
        # Turn 1: Always Spawn
        if self._turn_count == 1:
            self.current_intention = self.intentions["Spawn"]
            return
        
        # Turn 4: Always Mega Debuff (once)
        if self._turn_count == 4 and not self._used_mega_debuff:
            self._used_mega_debuff = True
            self.current_intention = self.intentions["Mega Debuff"]
            return
        
        # Get last move
        last = self.history_intentions[-1] if self.history_intentions else None
        
        # Count consecutive Fireball uses
        fireball_consecutive = 0
        for move in reversed(self.history_intentions):
            if move == "Fireball":
                fireball_consecutive += 1
            else:
                break
        
        # Determine valid moves
        can_spawn = self._count_torch_heads() < 2
        can_buff = last != "Buff"
        can_fireball = fireball_consecutive < 2
        
        # Pattern based on Torch Head count
        torch_heads = self._count_torch_heads()
        
        if torch_heads >= 2:
            # Both Torch Heads alive: 70% Fireball, 30% Buff
            if can_fireball and can_buff:
                if random.random() < 0.70:
                    self.current_intention = self.intentions["Fireball"]
                else:
                    self.current_intention = self.intentions["Buff"]
            elif can_fireball:
                self.current_intention = self.intentions["Fireball"]
            else:
                self.current_intention = self.intentions["Buff"]
        else:
            # 0-1 Torch Heads: 25% Spawn, 45% Fireball, 30% Buff
            if can_spawn and can_fireball and can_buff:
                roll = random.random()
                if roll < 0.25:
                    self.current_intention = self.intentions["Spawn"]
                elif roll < 0.70:
                    self.current_intention = self.intentions["Fireball"]
                else:
                    self.current_intention = self.intentions["Buff"]
            elif can_fireball and can_buff:
                if random.random() < 0.60:
                    self.current_intention = self.intentions["Fireball"]
                else:
                    self.current_intention = self.intentions["Buff"]
            elif can_fireball:
                self.current_intention = self.intentions["Fireball"]
            elif can_buff:
                self.current_intention = self.intentions["Buff"]
            else:
                self.current_intention = self.intentions["Spawn"]
