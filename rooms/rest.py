"""
Rest room implementation.
"""
from actions.card import ChooseRemoveCardAction, ChooseUpgradeCardAction
from actions.display import SelectAction, DisplayTextAction
from actions.health import HealAction
from actions.reward import AddRelicAction, AddRandomRelicAction
from actions.room import TriggerRelicAction, LeaveRoomAction
from engine.game_state import game_state
from localization import LocalStr
from rooms.base import Room
from utils.option import Option
from utils.registry import register
from utils.types import RarityType, RoomType


def _has_relic(relic_name: str) -> bool:
    """Check if player has a specific relic"""
    if not game_state.player:
        return False
    
    target = relic_name.strip().lower().replace(" ", "").replace("_", "").replace("-", "")
    
    for relic in game_state.player.relics:
        relic_id = getattr(relic, "idstr", None)
        if relic_id and relic_id.strip().lower().replace(" ", "").replace("_", "").replace("-", "") == target:
            return True
        relic_name_attr = getattr(relic, "name", None)
        if relic_name_attr and relic_name_attr.strip().lower().replace(" ", "").replace("_", "").replace("-", "") == target:
            return True
    
    return False


@register("room")
class RestRoom(Room):
    """Rest site room where player can rest, upgrade cards, or recall Ruby Key"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.room_type = RoomType.REST
        self.localization_prefix = "rooms"
    
    def init(self):
        """Initialize the rest room"""
        # Handle Eternal Feather - heal on enter
        if _has_relic("EternalFeather"):
            deck = game_state.player.card_manager.get_pile('deck')
            deck_size = len(deck)
            heal_amount = (deck_size // 5) * 3
            if heal_amount > 0:
                self.action_queue.add_action(HealAction(amount=heal_amount))
    
    def enter(self) -> str:
        """Enter the rest room and handle rest options"""
        # Display entry message
        self.action_queue.add_action(DisplayTextAction(
            text_key="rooms.rest.enter"
        ))
        
        # Main rest loop
        while not self.should_leave:
            # Build rest options
            self._build_rest_menu()
            
            # Execute actions
            result = self.execute_actions()
            
            # Check for game end
            if result in ("DEATH", "WIN"):
                return result
            
            # Rebuild menu if not leaving
            if not self.should_leave:
                self.action_queue.clear()
        
        return None
    
    def leave(self):
        """Leave the rest room"""
        super().leave()
        # Handle Ancient Tea Set - add energy next turn
        if _has_relic("AncientTeaSet"):
            # Add 2 energy for next combat
            # todo: Would need to track this in game state
            pass
    
    def _build_rest_menu(self):
        """Build the rest site menu options"""
        options = []
        
        # Rest option
        can_rest = not (_has_relic("CoffeeDripper") or _has_relic("MarkOfTheBloom"))
        if can_rest:
            heal_amount = int(game_state.player.max_hp * 0.30)
            if _has_relic("RegalPillow"):
                heal_amount += 15
            options.append(Option(
                name=self.local("RestRoom.rest", amount=heal_amount),
                actions=[HealAction(amount=heal_amount)]
            ))
        
        # Smith option (upgrade card)
        can_smith = not _has_relic("FusionHammer")
        if can_smith:
            deck = game_state.player.card_manager.get_pile('deck')
            for card in deck:
                if card.can_upgrade():
                    can_smith = True
                    break
        if can_smith:
            options.append(Option(
                name=self.local("RestRoom.smith"),
                actions=[ChooseUpgradeCardAction(pile="deck")]
            ))
        
        # todo: Recall option (Ruby Key) - disabled for now
        # if _can_recall():
        #     options.append(Option(
        #         name=self.local("RestRoom.recall"),
        #         actions=[AddRelicAction(relic="RubyKey"), LeaveRestAction()]
        #     ))
        
        # Special relic options (Girya, Peace Pipe, Shovel)
        if _has_relic("Girya"):
            options.append(Option(
                name=self.local("RestRoom.lift"),
                actions=[TriggerRelicAction(relic_name="Lift")], # todo
            ))
        
        if _has_relic("PeacePipe"):
            options.append(Option(
                name=self.local("RestRoom.toke"),
                actions=[ChooseRemoveCardAction(pile="deck")]
            ))
        
        if _has_relic("Shovel"):
            options.append(Option(
                name=self.local("RestRoom.dig"),
                actions=[AddRandomRelicAction(rarities=[RarityType.COMMON, RarityType.UNCOMMON, RarityType.RARE])]
            ))
        
        # Skip option
        options.append(Option(
            name=self.local("RestRoom.skip"),
            actions=[]
        ))
        
        # Add selection action to queue
        self.action_queue.add_action(SelectAction(
            title=self.local("RestRoom.title"),
            options=options
        ))
        self.action_queue.add_action(
            LeaveRoomAction(room=self)
        )