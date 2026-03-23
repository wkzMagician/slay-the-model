"""
Rest room implementation.
"""
from actions.card import (
    ChooseObtainCardAction,
    ChooseRemoveCardAction,
    ChooseUpgradeCardAction,
)
from actions.display import InputRequestAction, DisplayTextAction
from actions.reward import AddRelicAction, AddRandomRelicAction
from actions.misc import LeaveRoomAction, _has_relic
from utils.result_types import GameStateResult, MultipleActionsResult, NoneResult
from engine.game_state import game_state
from localization import LocalStr
from rooms.base import Room, BaseResult
from utils.option import Option
from utils.registry import register
from utils.types import RarityType, RoomType
from actions.combat import HealAction, TriggerRelicAction

@register("room")
class RestRoom(Room):
    """Rest site room where player can rest, upgrade cards, or recall Ruby Key"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.room_type = RoomType.REST
        self.localization_prefix = "rooms"
    
    def init(self):
        """Initialize the rest room"""
        pass
    
    def enter(self) -> BaseResult:
        """Enter rest room and return the initial rest actions."""
        actions = []

        if _has_relic("EternalFeather", game_state):
            deck = game_state.player.card_manager.get_pile('deck')
            deck_size = len(deck)
            heal_amount = (deck_size // 5) * 3
            if heal_amount > 0:
                actions.append(HealAction(amount=heal_amount))

        actions.append(DisplayTextAction(text_key="rooms.RestRoom.enter"))
        actions.append(self._build_rest_menu())
        return MultipleActionsResult(actions)
    
    def leave(self):
        """Leave the rest room"""
        super().leave()
        # Handle Ancient Tea Set - add energy next turn
        if _has_relic("AncientTeaSet", game_state):
            # set relic available for next combat
            for relic in game_state.player.relics:
                if getattr(relic, "idstr", "").lower() == "ancientteaset":
                    relic.is_rest_last_room = True
                    break
    
    def _build_rest_menu(self):
        """Build the rest site menu options"""
        options = []
        
        # Rest option - heal 30% of max HP
        heal_amount = game_state.player.max_hp // 10 * 3
        for relic in game_state.player.relics:
            if hasattr(relic, "modify_rest_heal"):
                heal_amount = relic.modify_rest_heal(heal_amount)
        rest_actions = [HealAction(amount=heal_amount)]
        if _has_relic("DreamCatcher", game_state):
            rest_actions.append(
                ChooseObtainCardAction(
                    total=3,
                    namespace=game_state.player.namespace,
                    encounter_type="normal",
                    use_rolling_offset=True,
                )
            )
        rest_actions.append(LeaveRoomAction(room=self))
        options.append(Option(
            name=self.local("rest"),
            actions=rest_actions
        ))


        can_smith = not _has_relic("FusionHammer", game_state)
        if can_smith:
            can_smith = False
            deck = game_state.player.card_manager.get_pile('deck')
            for card in deck:
                if card.can_upgrade():
                    can_smith = True
                    break
        if can_smith:
            options.append(Option(
                name=self.local("smith"),
                actions=[ChooseUpgradeCardAction(pile="deck"), LeaveRoomAction(room=self)]
            ))
        
        # feature: Recall option (Ruby Key) - disabled for now
        # if _can_recall():
        #     options.append(Option(
        #         name=self.local("RestRoom.recall"),
        #         actions=[AddRelicAction(relic="RubyKey"), LeaveRestAction()]
        #     ))
        
        # Special relic options (Girya, Peace Pipe, Shovel)
        if _has_relic("Girya", game_state):
            # Check if Girya can still be used
            for relic in game_state.player.relics:
                if getattr(relic, "idstr", None) == "Girya":
                    if hasattr(relic, "can_use_at_rest") and relic.can_use_at_rest():
                        options.append(Option(
                            name=self.local("lift"),
                            actions=[TriggerRelicAction(relic_name="Lift"), LeaveRoomAction(room=self)],
                        ))
                    break
        
        if _has_relic("PeacePipe", game_state):
            options.append(Option(
                name=self.local("toke"),
                actions=[ChooseRemoveCardAction(pile="deck"), LeaveRoomAction(room=self)]
            ))
        
        if _has_relic("Shovel", game_state):
            options.append(Option(
                name=self.local("dig"),
                actions=[AddRandomRelicAction(rarities=[RarityType.COMMON, RarityType.UNCOMMON, RarityType.RARE]), LeaveRoomAction(room=self)]
            ))
        
        # Skip option
        options.append(Option(
            name=self.local("skip"),
            actions=[LeaveRoomAction(room=self)]
        ))
        
        return InputRequestAction(
            title=self.local("title"),
            options=options
        )

    def _create_options(self):
        """Create and return rest options (for testing)."""
        options = []

        # Rest option - heal 30% of max HP
        heal_amount = game_state.player.max_hp // 10 * 3
        for relic in game_state.player.relics:
            if hasattr(relic, "modify_rest_heal"):
                heal_amount = relic.modify_rest_heal(heal_amount)
        rest_actions = [HealAction(amount=heal_amount)]
        if self._check_relic("DreamCatcher"):
            rest_actions.append(
                ChooseObtainCardAction(
                    total=3,
                    namespace=game_state.player.namespace,
                    encounter_type="normal",
                    use_rolling_offset=True,
                )
            )
        rest_actions.append(LeaveRoomAction(room=self))
        options.append(Option(
            name=self.local("rest"),
            actions=rest_actions
        ))

        can_smith = not self._check_relic("FusionHammer")
        if can_smith:
            can_smith = False
            deck = game_state.player.card_manager.get_pile('deck')
            for card in deck:
                if card.can_upgrade():
                    can_smith = True
                    break
        if can_smith:
            options.append(Option(
                name=self.local("smith"),
                actions=[ChooseUpgradeCardAction(pile="deck"), LeaveRoomAction(room=self)]
            ))

        # Special relic options (Girya, Peace Pipe, Shovel)
        if self._check_relic("Girya"):
            options.append(Option(
                name=self.local("lift"),
                actions=[TriggerRelicAction(relic_name="Lift"), LeaveRoomAction(room=self)],
            ))

        if self._check_relic("PeacePipe"):
            options.append(Option(
                name=self.local("toke"),
                actions=[ChooseRemoveCardAction(pile="deck"), LeaveRoomAction(room=self)]
            ))

        if self._check_relic("Shovel"):
            options.append(Option(
                name=self.local("dig"),
                actions=[AddRandomRelicAction(rarities=[RarityType.COMMON, RarityType.UNCOMMON, RarityType.RARE]), LeaveRoomAction(room=self)]
            ))

        # Skip option
        options.append(Option(
            name=self.local("skip"),
            actions=[LeaveRoomAction(room=self)]
        ))

        return options

    def _check_relic(self, relic_name: str) -> bool:
        """Check if player has a specific relic."""
        return _has_relic(relic_name, game_state)
