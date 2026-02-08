"""
Combat room implementation - manages Combat instance execution.
"""
from typing import TYPE_CHECKING

from actions.display import DisplayTextAction
from utils.result_types import NoneResult
from actions.reward import AddGoldAction, AddRandomPotionAction
from actions.card import AddCardAction, AddRandomCardAction
from utils.result_types import GameStateResult
from engine.combat import Combat
from rooms.base import Room, BaseResult
from utils.registry import register
from utils.types import RoomType, RarityType, CardType

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
        )
    
    def enter(self) -> BaseResult:
        """Enter combat room and execute combat"""
        from engine.game_state import game_state

        # Display room entry message
        if self.is_boss:
            game_state.action_queue.add_action(DisplayTextAction(
                text_key="rooms.combat.boss_enter"
            ))
        elif self.is_elite:
            game_state.action_queue.add_action(DisplayTextAction(
                text_key="rooms.combat.elite_enter"
            ))
        else:
            game_state.action_queue.add_action(DisplayTextAction(
                text_key="rooms.combat.enter"
            ))

        # Execute combat
        assert self.combat is not None
        result = self.combat.start()
        
        # Handle combat result
        if result.state == "COMBAT_WIN":
            self._handle_victory()
        # ESCAPE：没有reward
        
        if result.state == "GAME_LOSE":
            return result
        else:
            return game_state.execute_all_actions()
    
    def leave(self):
        """Leave the combat room"""
        super().leave()
        # Clean up combat state
        if self.combat:
            self.combat = None
    
    def _handle_victory(self):
        """Handle combat victory - add rewards"""
        from engine.game_state import game_state

        # Calculate gold reward
        gold_amount = self._calculate_gold_reward()
        if gold_amount > 0:
            game_state.action_queue.add_action(AddGoldAction(amount=gold_amount))

        # Add card reward (non-boss)
        if not self.is_boss:
            game_state.action_queue.add_action(AddRandomCardAction(
                pile="hand",
                card_type=CardType.ATTACK,
                rarity=RarityType.COMMON
            ))

        # Add potion reward (elites and bosses)
        if self.is_elite or self.is_boss:
            game_state.action_queue.add_action(AddRandomPotionAction(
                character=game_state.player.character
            ))

        # Display victory message
        game_state.action_queue.add_action(DisplayTextAction(
            text_key="rooms.combat.victory"
        ))
    
    def _calculate_gold_reward(self) -> int:
        """
        Calculate gold reward based on enemy difficulty.
        
        Returns:
            Gold amount to award
        """
        # todo: 价格波动
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