"""
Victory room - handles end-of-act victory and Act 4 transition logic.

In Act 3:
- Checks if player has all 3 keys (ruby, emerald, sapphire)
- With keys: Transitions to Act 4
- Without keys: Game victory

In Act 4:
- Final victory (Corrupt Heart defeated)
"""
from utils.result_types import BaseResult, GameStateResult, NoneResult
from localization import t
from rooms.base import Room
from utils.types import RoomType


class VictoryRoom(Room):
    """
    Victory room that checks keys and handles Act 4 transition.
    
    - Act 3 without keys: Game victory
    - Act 3 with keys: Transition to Act 4
    - Act 4: Final game victory
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.room_type = RoomType.VICTORY
    
    def enter(self) -> BaseResult:
        from engine.game_state import game_state
        
        if game_state.current_act == 4:
            self._handle_act4_victory()
            return GameStateResult(state="WIN")
        
        if game_state.current_act == 3:
            if game_state.has_all_keys:
                self._handle_act4_transition()
                return NoneResult()
            else:
                self._handle_act3_victory()
                return GameStateResult(state="WIN")
        
        return NoneResult()
    
    def _handle_act3_victory(self):
        from engine.game_state import game_state
        print(t('ui.act3_victory', 
               default='\n=== The Spire Falls! ==='))
        print(t('ui.act3_victory_message',
               default='You have defeated the Act 3 boss and conquered the Spire!'))
        print(t('ui.keys_hint',
               default='(Collect all three keys to challenge the Heart in Act 4)'))
    
    def _handle_act4_transition(self):
        from engine.game_state import game_state
        print(t('ui.keys_collected',
               default='\n=== The Three Keys Resonate! ==='))
        print(t('ui.keys_collected_message',
               default='With the Ruby, Emerald, and Sapphire keys in hand,'))
        print(t('ui.heart_entrance',
               default='you unlock the path to the Corrupt Heart...'))
    
    def _handle_act4_victory(self):
        print(t('ui.heart_defeated',
               default='\n=== THE CORRUPT HEART FALLS! ==='))
        print(t('ui.heart_defeated_message',
               default='The source of the Spire\'s corruption is destroyed!'))
        print(t('ui.true_victory',
               default='You have achieved TRUE VICTORY!'))
