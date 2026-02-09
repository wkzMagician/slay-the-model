"""
Combat room implementation - manages Combat instance execution.
"""
from typing import TYPE_CHECKING, List

from actions.base import Action
from actions.display import DisplayTextAction
from utils.result_types import MultipleActionsResult, NoneResult
from actions.reward import AddGoldAction, AddRandomPotionAction
from actions.card import AddCardAction, AddRandomCardAction
from utils.result_types import GameStateResult
from engine.combat import Combat
from rooms.base import Room, BaseResult
from utils.registry import register
from utils.types import RoomType, RarityType, CardType, CombatType

@register("room")
class CombatRoom(Room):
    """Combat room - manages the creation and execution of Combat"""

    def __init__(self, enemies=None, room_type=RoomType.MONSTER, **kwargs):
        super().__init__(**kwargs)
        self.room_type = room_type
        self.enemies = enemies or []
        self.combat = None
    
    def init(self):
        """Initialize the combat instance"""
        # Determine combat type based on room type
        combat_type = CombatType.BOSS if self.room_type == RoomType.BOSS else CombatType.ELITE if self.room_type == RoomType.ELITE else CombatType.NORMAL
        
        self.combat = Combat(
            enemies=self.enemies,
            combat_type=combat_type
        )
    
    def enter(self) -> BaseResult:
        """Enter combat room and execute combat"""
        from engine.game_state import game_state
        actions = []

        # Display room entry message
        if self.room_type == RoomType.BOSS:
            actions.append(DisplayTextAction(text_key="rooms.combat.boss_enter"))
        elif self.room_type == RoomType.ELITE:
            actions.append(DisplayTextAction(text_key="rooms.combat.elite_enter"))
        else:
            actions.append(DisplayTextAction(text_key="rooms.combat.enter"))

        # Execute combat
        assert self.combat is not None
        result = self.combat.start()
        
        # Handle combat result
        if result.state == "COMBAT_WIN":
            victory_actions = self._handle_victory()
            if victory_actions:
                actions.extend(victory_actions)
        # ESCAPE：没有reward
        
        if result.state == "GAME_LOSE":
            return result
        else:
            if actions:
                return MultipleActionsResult(actions)
            return NoneResult()
    
    def leave(self):
        """Leave the combat room"""
        super().leave()
        # Clean up combat state
        if self.combat:
            self.combat = None
    
    def _handle_victory(self) -> List['Action']:
        """Handle combat victory - add rewards"""
        from engine.game_state import game_state
        actions = []

        # Calculate gold reward
        gold_amount = self._calculate_gold_reward()
        if gold_amount > 0:
            actions.append(AddGoldAction(amount=gold_amount))

        # Add card reward (non-boss)
        if self.room_type != RoomType.BOSS:
            actions.append(AddRandomCardAction(
                pile="hand",
                card_type=CardType.ATTACK,
                rarity=RarityType.COMMON
            ))

        # Add potion reward (elites and bosses)
        if self.room_type in (RoomType.ELITE, RoomType.BOSS):
            actions.append(AddRandomPotionAction(
                character=game_state.player.character
            ))

        # Display victory message
        actions.append(DisplayTextAction(text_key="rooms.combat.victory"))

        return actions
    
    def _calculate_gold_reward(self) -> int:
        """
        Calculate gold reward based on enemy difficulty.
        
        Returns:
            Gold amount to award
        """
        # todo: 价格波动
        if self.room_type == RoomType.BOSS:
            return 150  # Base boss gold
        elif self.room_type == RoomType.ELITE:
            return 50  # Base elite gold
        else:
            # Normal enemy gold
            total_gold = 0
            for enemy in self.enemies:
                # Simple calculation: base gold from enemy
                total_gold += getattr(enemy, 'gold_reward', 15)
            return total_gold