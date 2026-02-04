"""
Combat room implementation - manages Combat instance execution.
"""
from actions.display import DisplayTextAction
from actions.reward import AddGoldAction, AddCardAction, AddRandomPotionAction
from engine.combat import Combat
from engine.game_state import game_state
from rooms.base import Room
from utils.registry import register
from utils.types import RoomType


@register("room")
class CombatRoom(Room):
    """Combat room - manages the creation and execution of Combat"""

    def __init__(self, enemies=None, is_elite=False, is_boss=False, **kwargs):
        super().__init__(**kwargs)
        self.room_type = RoomType.BOSS if is_boss else RoomType.ELITE if is_elite else RoomType.MONSTER
        self.enemies = enemies or []
        self.is_elite = is_elite
        self.is_boss = is_boss
        self.combat = None
    
    def init(self):
        """Initialize the combat instance"""
        self.combat = Combat(
            enemies=self.enemies,
            is_elite=self.is_elite,
            is_boss=self.is_boss
        )
    
    def enter(self) -> str:
        """Enter the combat room and execute combat"""
        # Display room entry message
        if self.is_boss:
            self.action_queue.add_action(DisplayTextAction(
                text_key="rooms.combat.boss_enter"
            ))
        elif self.is_elite:
            self.action_queue.add_action(DisplayTextAction(
                text_key="rooms.combat.elite_enter"
            ))
        else:
            self.action_queue.add_action(DisplayTextAction(
                text_key="rooms.combat.enter"
            ))
        
        # Execute the combat
        result = self.combat.start()
        
        # Handle combat result
        if result == "WIN":
            self._handle_victory()
        elif result == "DEATH":
            # Death is handled by game flow
            pass
        
        return result
    
    def leave(self):
        """Leave the combat room"""
        super().leave()
        # Clean up combat state
        if self.combat:
            self.combat = None
    
    def _handle_victory(self):
        """Handle combat victory - add rewards"""
        # Calculate gold reward
        gold_amount = self._calculate_gold_reward()
        if gold_amount > 0:
            self.action_queue.add_action(AddGoldAction(amount=gold_amount))
        
        # Add card reward (non-boss)
        if not self.is_boss:
            self.action_queue.add_action(AddCardAction(random_from_pool=True))
        
        # Add potion reward (elites and bosses)
        if self.is_elite or self.is_boss:
            self.action_queue.add_action(AddRandomPotionAction())
        
        # Display victory message
        self.action_queue.add_action(DisplayTextAction(
            text_key="rooms.combat.victory"
        ))
    
    def _calculate_gold_reward(self) -> int:
        """
        Calculate gold reward based on enemy difficulty.
        
        Returns:
            Gold amount to award
        """
        if self.is_boss:
            return 150  # Base boss gold
        elif self.is_elite:
            return 50  # Base elite gold
        else:
            # Normal enemy gold
            total_gold = 0
            for enemy in self.enemies:
                # Simple calculation: base gold from enemy
                total_gold += getattr(enemy, 'gold_reward', 15)
            return total_gold