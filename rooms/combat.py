"""
Combat room implementation - manages Combat instance execution.
"""
from typing import TYPE_CHECKING, List

from actions.base import Action
from actions.display import DisplayTextAction
from utils.result_types import MultipleActionsResult, NoneResult
from actions.reward import AddGoldAction, AddRandomPotionAction
from actions.card import AddCardAction, AddRandomCardAction, ChooseAddRandomCardAction
from utils.result_types import GameStateResult
from engine.combat import Combat
from rooms.base import Room, BaseResult
from utils.registry import register
from utils.types import RoomType, RarityType, CardType, CombatType

@register("room")
class CombatRoom(Room):
    """Combat room - manages the creation and execution of Combat"""

    def __init__(self, enemies=None, room_type=RoomType.MONSTER, encounter_name: str = "", **kwargs):
        super().__init__(**kwargs)
        self.room_type = room_type
        self.enemies = enemies or []
        self.encounter_name = encounter_name  # Track encounter name for history
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

        # Increment normal encounter counter and track history (only for normal monsters, not elites/bosses)
        if self.room_type == RoomType.MONSTER:
            game_state.normal_encounters_fought += 1
            if self.encounter_name:
                game_state.encounter_history.append(self.encounter_name)

        # Track elite history
        if self.room_type == RoomType.ELITE:
            if self.encounter_name:
                game_state.elite_history.append(self.encounter_name)

        # Calculate gold reward
        gold_amount = self._calculate_gold_reward()
        if gold_amount > 0:
            actions.append(AddGoldAction(amount=gold_amount))

        # Add card reward (non-boss)
        if self.room_type != RoomType.BOSS:
            # 3 choose 1, rarity determined by encounter type
            actions.append(ChooseAddRandomCardAction(
                pile='deck',
                total=3,
                namespace=game_state.player.namespace
            ))
        else:  # boss - 3 rare cards
            actions.append(ChooseAddRandomCardAction(
                pile='deck',
                total=3,
                namespace=game_state.player.namespace,
                rarity=RarityType.RARE
            ))

        # Add potion reward with probability check
        # Base 40% chance, -10% after drop, +10% after no drop
        # White Beast Statue: always drop
        from actions.misc import _has_relic

        if _has_relic("White Beast Statue", game_state):
            # Always drop with White Beast Statue
            actions.append(AddRandomPotionAction(
                character=game_state.player.character
            ))
            game_state.potion_drop_chance = max(10, game_state.potion_drop_chance - 10)
        else:
            import random as rd
            if rd.randint(1, 100) <= game_state.potion_drop_chance:
                actions.append(AddRandomPotionAction(
                    character=game_state.player.character
                ))
                game_state.potion_drop_chance = max(10, game_state.potion_drop_chance - 10)
            else:
                game_state.potion_drop_chance = min(90, game_state.potion_drop_chance + 10)

        # Display victory message
        actions.append(DisplayTextAction(text_key="rooms.combat.victory"))

        return actions
    
    def _calculate_gold_reward(self) -> int:
        """
        Calculate gold reward based on enemy difficulty.
        
        Returns:
            Gold amount to award
        
        Normal enemy gold with random fluctuation: 10-20
        Elite enemy gold with random fluctuation: 25-35
        Boss gold with random fluctuation: 95-105
        """
        import random as rd

        if self.room_type == RoomType.BOSS:
            return rd.randint(95, 105)
        elif self.room_type == RoomType.ELITE:
            return rd.randint(25, 35)
        else:
            return rd.randint(10, 20)