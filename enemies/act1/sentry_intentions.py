"""Sentry elite enemy intentions."""

from typing import List, TYPE_CHECKING

from enemies.intention import Intention

if TYPE_CHECKING:
    from enemies.base import Enemy
    from actions.base import Action


class BoltIntention(Intention):
    """Bolt - Add 2 Dazed cards to player's discard pile (3 on A3+)."""
    
    def __init__(self, enemy: 'Enemy', dazed_count: int = 2):
        super().__init__("bolt", enemy)
        self.dazed_count = dazed_count
    
    def execute(self) -> List['Action']:
        """Execute Bolt: add Dazed cards to player's discard pile."""
        from actions.card import AddCardAction
        from cards.colorless.dazed import Dazed
        from engine.game_state import game_state
        
        actions = []
        
        if game_state and game_state.player:
            for _ in range(self.dazed_count):
                actions.append(
                    AddCardAction(
                        card=Dazed(),
                        dest_pile="discard_pile",
                        source="enemy"
                    )
                )
        
        return actions


class BeamIntention(Intention):
    """Beam - Deal 9 damage."""
    
    def __init__(self, enemy: 'Enemy', damage: int = 9):
        super().__init__("beam", enemy)
        self.base_damage = damage
    
    def execute(self) -> List['Action']:
        """Execute Beam: deal damage."""
        from actions.combat import AttackAction
        from engine.game_state import game_state
        
        if not game_state or not game_state.player:
            return []
        
        return [
            AttackAction(
                damage=self.base_damage,
                target=game_state.player,
                source=self.enemy,
                damage_type="attack",
            )
        ]
