# -*- coding: utf-8 -*-
"""
Display handler - manages content for the display panel.
Handles player info, map view, combat view, and room-specific displays.
"""
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from engine.game_state import GameState
    from engine.combat import Combat
    from rooms.base import Room


class DisplayHandler:
    """Handles display panel content generation."""
    
    def __init__(self, app):
        self._app = app
    
    def update_player_info(self, gs: 'GameState'):
        """Update player info section."""
        self._app.update_player_info(gs.player, gs)
    
    def display_map(self, gs: 'GameState'):
        """Display map for node selection."""
        from localization import t
        
        lines = []
        lines.append(t("ui.map_title", default="[ MAP ]"))
        lines.append("─" * 38)
        
        if hasattr(gs, 'map_manager') and gs.map_manager:
            lines.append(gs.map_manager.get_map_text_for_human())
        else:
            lines.append(t("ui.no_map", default="No map available."))
        
        self._app.update_display_content("\n".join(lines))
    
    def display_combat(self, combat: 'Combat', gs: 'GameState'):
        """Display combat state."""
        from localization import t
        player = gs.player
        hand = player.card_manager.get_pile("hand")
        draw_pile = player.card_manager.get_pile("draw_pile")
        discard_pile = player.card_manager.get_pile("discard_pile")
        
        lines = []
        
        lines.append(t("combat.title", default="[ COMBAT ]"))
        lines.append("─" * 38)
        
        lines.append("")
        lines.append(t("combat.enemies", default="Enemies:"))
        for enemy in combat.enemies:
            if not enemy.is_dead:
                hp_str = f"HP: {enemy.hp}/{enemy.max_hp}"
                block_str = f"Block: {enemy.block}" if enemy.block > 0 else ""
                intention_str = ""
                if enemy.current_intention:
                    intention_str = f"[{enemy.current_intention.name}]"
                lines.append(f"  • {enemy.name} {hp_str} {block_str} {intention_str}")
        
        lines.append("")
        lines.append(t("combat.hand", default="Hand:"))
        for i, card in enumerate(hand):
            cost = getattr(card, "cost_for_turn", getattr(card, "cost", None))
            cost_str = f"[{cost}]" if cost is not None else ""
            if hasattr(card, "local"):
                card_name = card.local("name").resolve()
            else:
                card_name = getattr(card, "name", card.__class__.__name__)
            lines.append(f"  {i + 1}. {card_name} {cost_str}")
        
        lines.append("")
        lines.append(f"Draw: {len(draw_pile)} | Discard: {len(discard_pile)}")
        
        if player.powers:
            lines.append("")
            lines.append(t("combat.powers", default="Powers:"))
            for power in player.powers:
                amount = getattr(power, "amount", None)
                lines.append(f"  • {power.name} ({amount})")
        
        self._app.update_display_content("\n".join(lines))
        self.update_player_info(gs)
    
    def display_room(self, room: 'Room', gs: 'GameState'):
        """Display room-specific content."""
        room_type = type(room).__name__
        
        if room_type == "RestRoom":
            self._display_rest_room(room, gs)
        elif room_type == "ShopRoom":
            self._display_shop_room(room, gs)
        elif room_type == "TreasureRoom":
            self._display_treasure_room(room, gs)
        elif room_type == "EventRoom":
            self._display_event_room(room, gs)
        else:
            self._display_generic_room(room, gs)
    
    def _display_rest_room(self, room, gs):
        from localization import t
        lines = [t("rooms.rest.title", default="[ REST ]")]
        lines.append("─" * 38)
        lines.append("")
        lines.append(t("rooms.rest.description", default="Choose to rest and heal, or upgrade a card."))
        self._app.update_display_content("\n".join(lines))
    
    def _display_shop_room(self, room, gs):
        from localization import t
        lines = [t("rooms.shop.title", default="[ SHOP ]")]
        lines.append("─" * 38)
        lines.append("")
        lines.append(t("rooms.shop.gold", default=f"Your Gold: {gs.player.gold}"))
        self._app.update_display_content("\n".join(lines))
    
    def _display_treasure_room(self, room, gs):
        from localization import t
        lines = [t("rooms.treasure.title", default="[ TREASURE ]")]
        lines.append("─" * 38)
        lines.append("")
        lines.append(t("rooms.treasure.description", default="A chest awaits!"))
        self._app.update_display_content("\n".join(lines))
    
    def _display_event_room(self, room, gs):
        from localization import t
        lines = [t("rooms.event.title", default="[ EVENT ]")]
        lines.append("─" * 38)
        lines.append("")
        if hasattr(room, 'event') and room.event:
            lines.append(str(room.event.name))
        self._app.update_display_content("\n".join(lines))
    
    def _display_generic_room(self, room, gs):
        from localization import t
        lines = [t("rooms.title", default=f"[ {type(room).__name__} ]")]
        lines.append("─" * 38)
        self._app.update_display_content("\n".join(lines))
    
    def clear(self):
        """Clear display panel."""
        self._app.update_display_content("")
