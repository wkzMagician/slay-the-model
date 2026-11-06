"""Book of Stabbing - Act 2 Elite enemy."""
from engine.random_streams import get_rng

from typing import List

from enemies.act2.book_of_stabbing_intentions import BigStab, MultiStab
from enemies.base import Enemy
from utils.types import EnemyType


class BookOfStabbing(Enemy):
    """Elite enemy found in Act 2.
    
    Multi Stab deals increasing damage the more it's used.
    Pattern: 15% Big Stab, 85% Multi Stab.
    Cannot use Multi Stab 3 times in a row.
    Cannot use Big Stab twice in a row.
    """
    
    enemy_type = EnemyType.ELITE
    
    def __init__(self):
        from engine.game_state import game_state

        ascension = getattr(game_state, "ascension", 0)
        hp_range = (168, 172) if ascension >= 8 else (160, 164)
        super().__init__(hp_range=hp_range)
        self._selected_after_turn = -1
        self.multi_stab_count = 0  # Number of times Multi Stab used
        
        # Register intentions
        self.add_intention(MultiStab(self))
        self.add_intention(BigStab(self))

    def on_combat_start(self, floor: int):
        from powers.definitions.painful_stabs import PainfulStabsPower

        super().on_combat_start(floor)
        if not self.has_power("Painful Stabs"):
            self.add_power(PainfulStabsPower(owner=self))
    
    def determine_next_intention(self, floor: int):
        """Determine next intention based on pattern."""
        from engine.game_state import game_state

        ascension = getattr(game_state, "ascension", 0)
        completed = len(self.history_intentions)
        if self._selected_after_turn == completed:
            return self.current_intention
        self._selected_after_turn = completed
        # Get last move
        last = self.history_intentions[-1] if self.history_intentions else None
        
        # Count consecutive Multi Stab uses
        multi_stab_consecutive = 0
        for move in reversed(self.history_intentions):
            if move == "Multi Stab":
                multi_stab_consecutive += 1
            else:
                break
        
        # Determine valid moves
        can_multi_stab = multi_stab_consecutive < 2
        can_big_stab = last != "Big Stab"
        
        # Select move based on weights
        if not can_big_stab:
            # Must use Multi Stab
            if can_multi_stab:
                self.current_intention = self.intentions["Multi Stab"]
        elif not can_multi_stab:
            # Must use Big Stab
            if can_big_stab:
                self.current_intention = self.intentions["Big Stab"]
        else:
            # Both available - 15% Big Stab, 85% Multi Stab
            if get_rng("ai").random() < 0.15:
                self.current_intention = self.intentions["Big Stab"]
            else:
                self.current_intention = self.intentions["Multi Stab"]

        if self.current_intention is None:
            self.current_intention = self.intentions["Multi Stab"]

        if self.current_intention.name == "Multi Stab":
            self.intentions["Multi Stab"]._hits = self.multi_stab_count + 2
        if self.current_intention.name == "Big Stab" and ascension >= 18:
            self.multi_stab_count += 1

        return self.current_intention
    
    def execute_intention(self) -> None:
        """Execute current intention and update counter."""
        if not self.current_intention:
            return
        is_multi_stab = self.current_intention.name == "Multi Stab"
        super().execute_intention()
        if is_multi_stab:
            self.multi_stab_count += 1
