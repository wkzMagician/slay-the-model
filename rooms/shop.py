"""Shop room orchestration."""
from engine.runtime_events import emit_text
from rooms.base import BaseResult, Room
from rooms.shop_menu import build_shop_menu
from rooms.shop_state import game_state_has_relic, generate_shop_items
from utils.result_types import MultipleActionsResult
from utils.types import RoomType


_has_relic = game_state_has_relic


class ShopRoom(Room):
    """Shop room where the player can buy cards, relics, potions, and card removal."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.room_type = RoomType.MERCHANT
        self.localization_prefix = "rooms"
        self.items = []
        self.card_removal_price = 75
        self.card_removal_used = False

    def init(self):
        """Initialize the shop inventory."""
        self.items = self._generate_items()

    def enter(self) -> BaseResult:
        """Enter the shop and present the initial menu."""
        from engine.game_state import game_state
        from engine.messages import ShopEnteredMessage

        emit_text(self.local("enter", default="Enter the room"))
        game_state.publish_message(
            ShopEnteredMessage(owner=game_state.player, room=self, entities=[]),
            participants=list(game_state.player.relics),
        )
        return MultipleActionsResult([self._build_shop_menu()])

    def leave(self):
        """Leave the shop and reset single-visit state."""
        super().leave()
        self.card_removal_used = False

    def _generate_items(self):
        """Generate the current shop inventory."""
        from engine.game_state import game_state
        return generate_shop_items(player=getattr(game_state, "player", None))

    def _build_shop_menu(self):
        """Build the current shop menu."""
        from engine.game_state import game_state

        player = getattr(game_state, "player", None)
        player_gold = getattr(player, "gold", None) if player else None

        return build_shop_menu(
            title=self.local("title"),
            localize=self.local,
            items=self.items,
            player_gold=player_gold,
            ascension_level=getattr(game_state, "ascension_level", 0),
            card_removal_price=self.card_removal_price,
            card_removal_used=self.card_removal_used,
            has_smiling_mask=_has_relic("SmilingMask", game_state),
            has_membership_card=_has_relic("MembershipCard", game_state),
            has_the_courier=_has_relic("TheCourier", game_state),
            room=self,
        )
