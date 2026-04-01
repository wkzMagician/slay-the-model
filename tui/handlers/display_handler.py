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

    @staticmethod
    def _power_description_kwargs(power):
        """Build common localization kwargs for power descriptions."""
        kwargs = {}
        amount = getattr(power, "amount", None)
        duration = getattr(power, "duration", None)
        if amount is not None:
            kwargs["amount"] = amount
        if duration is not None:
            kwargs["duration"] = duration
        return kwargs
    
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
        import random
        from localization import t
        player = gs.player
        hand = player.card_manager.get_pile("hand")
        draw_pile = list(player.card_manager.get_pile("draw_pile"))
        discard_pile = list(player.card_manager.get_pile("discard_pile"))
        
        # Check for Frozen Eye relic
        has_frozen_eye = any(
            getattr(relic, "idstr", None) == "FrozenEye"
            for relic in gs.player.relics
        )
        
        lines = []
        
        lines.append(t("combat.title", default="[ COMBAT ]"))
        lines.append("─" * 38)
        
        lines.append("")
        lines.append(t("combat.enemies", default="Enemies:"))
        for enemy in combat.enemies:
            if not enemy.is_dead():
                hp_str = f"HP: {enemy.hp}/{enemy.max_hp}"
                block_str = f"Block: {enemy.block}" if enemy.block > 0 else ""
                intention_str = ""
                if enemy.current_intention:
                    intention_str = f"[{enemy.current_intention.description}]"
                # Use localized enemy name
                enemy_name = enemy.local("name").resolve() if hasattr(enemy, 'local') else enemy.name
                lines.append(f"  • {enemy_name} {hp_str} {block_str} {intention_str}")
                # Display enemy powers
                if hasattr(enemy, 'powers') and enemy.powers:
                    for power in enemy.powers:
                        power_name = power.local("name").resolve() if hasattr(power, 'local') else power.name
                        power_amount = power.amount if power.amount is not None and power.amount > 0 else None
                        if power_amount is not None:
                            lines.append(f"    - {power_name} x{power_amount}")
                        else:
                            lines.append(f"    - {power_name}")
        lines.append("")
        lines.append(t("combat.hand", default="Hand:"))
        for i, card in enumerate(hand):
            # Get cost display
            cost = getattr(card, "cost", None)
            if cost is not None:
                if cost == -1:  # COST_X
                    cost_str = "[X]"
                elif cost == -2:  # COST_UNPLAYABLE
                    cost_str = "[#]"
                else:
                    cost_str = f"[{cost}]"
            else:
                cost_str = ""
            
            # Get card display name (with upgrade indicator)
            card_name = card.display_name.resolve() if hasattr(card, 'display_name') else card.__class__.__name__
            
            # Get card type
            card_type = getattr(card, "card_type", None)
            type_str = card_type.value if card_type and hasattr(card_type, 'value') else ""
            
            # Show damage/block if applicable
            # stats_parts = []
            # if hasattr(card, 'damage') and card.damage > 0:
            #     stats_parts.append(f"DMG:{card.damage}")
            # if hasattr(card, 'block') and card.block > 0:
            #     stats_parts.append(f"BLK:{card.block}")
            # stats_str = f" ({', '.join(stats_parts)})" if stats_parts else ""
            
            lines.append(f"  {i + 1}. {cost_str} {card_name} [{type_str}] {card.description}")
        
        lines.append("")
        # Draw pile with card names (shuffled unless Frozen Eye)
        draw_display = list(reversed(draw_pile))
        if not has_frozen_eye:
            random.shuffle(draw_display)
        draw_names = ", ".join(card.display_name.resolve() for card in draw_display) if draw_display else t("ui.empty", default="Empty")
        lines.append(f"{t('ui.draw_pile', default='Draw Pile')} ({len(draw_pile)}): {draw_names}")
        
        # Discard pile with card names
        discard_names = ", ".join(card.display_name.resolve() for card in discard_pile) if discard_pile else t("ui.empty", default="Empty")
        lines.append(f"{t('ui.discard_pile', default='Discard Pile')} ({len(discard_pile)}): {discard_names}")
        
        # Exhaust pile (if any)
        exhaust_pile = list(player.card_manager.get_pile("exhaust_pile"))
        if exhaust_pile:
            exhaust_names = ", ".join(card.display_name.resolve() for card in exhaust_pile)
            lines.append(f"{t('ui.exhaust_pile', default='Exhaust')} ({len(exhaust_pile)}): {exhaust_names}")
        
        if player.powers:
            lines.append("")
            lines.append(t("combat.powers", default="Powers:"))
            for power in player.powers:
                # Get power name with localization
                power_name = power.local("name").resolve() if hasattr(power, 'local') else power.name
                # Show amount or duration
                display_amount = power.amount if power.amount is not None else getattr(power, 'duration', None)
                if display_amount is not None and display_amount > 0:
                    lines.append(f"  • {power_name} x{display_amount}")
                else:
                    lines.append(f"  • {power_name}")
        # Display relics
        if player.relics:
            lines.append("")
            lines.append(t("combat.relics", default="Relics:"))
            for relic in player.relics:
                relic_name = relic.local("name").resolve() if hasattr(relic, 'local') else relic.name
                lines.append(f"  • {relic_name}")
        
        # Display potions
        if player.potions:
            lines.append("")
            lines.append(t("combat.potions", default="Potions:"))
            for potion in player.potions:
                if potion is not None:
                    potion_name = potion.local("name").resolve() if hasattr(potion, 'local') else potion.name
                    lines.append(f"  • {potion_name}")
        
        # Detailed info section - descriptions (no duplicates)
        lines.append("")
        lines.append(t("combat.details", default="[ DETAILS ]"))
        lines.append("─" * 38)
        
        # Track what we've already shown to avoid duplicates
        shown_cards = set()
        shown_powers = set()
        shown_relics = set()
        
        # Card descriptions from piles (not hand - those are shown inline)
        all_pile_cards = []
        all_pile_cards.extend(draw_pile)
        all_pile_cards.extend(discard_pile)
        all_pile_cards.extend(exhaust_pile)
        
        card_details = []
        for card in all_pile_cards:
            card_id = card.__class__.__name__
            if card_id not in shown_cards:
                shown_cards.add(card_id)
                card_name = card.display_name.resolve() if hasattr(card, 'display_name') else card.__class__.__name__
                # Use combat_description for dynamic value resolution (e.g., {damage} -> 6)
                card_desc = ""
                if hasattr(card, 'combat_description'):
                    card_desc = card.combat_description.resolve()
                elif hasattr(card, 'description'):
                    card_desc = card.description.resolve()
                if card_desc:
                    card_details.append(f"  {card_name}: {card_desc}")
        
        if card_details:
            lines.append(t("combat.card_details", default="Cards:"))
            lines.extend(card_details)
        
        # Power descriptions (include enemy powers too)
        power_details = []
        # Player powers
        if player.powers:
            for power in player.powers:
                power_id = power.__class__.__name__
                if power_id not in shown_powers:
                    shown_powers.add(power_id)
                    power_name = power.local("name").resolve() if hasattr(power, 'local') else power.name
                    power_desc = (
                        power.local("description", **self._power_description_kwargs(power)).resolve()
                        if hasattr(power, 'local') else ""
                    )
                    # Only add if description exists and is not the raw key
                    if power_desc and not power_desc.startswith("powers."):
                        power_details.append(f"  {power_name}: {power_desc}")
                    else:
                        power_details.append(f"  {power_name}")
        # Enemy powers
        for enemy in combat.enemies:
            if not enemy.is_dead() and hasattr(enemy, 'powers') and enemy.powers:
                for power in enemy.powers:
                    power_id = power.__class__.__name__
                    if power_id not in shown_powers:
                        shown_powers.add(power_id)
                        power_name = power.local("name").resolve() if hasattr(power, 'local') else power.name
                        power_desc = (
                            power.local("description", **self._power_description_kwargs(power)).resolve()
                            if hasattr(power, 'local') else ""
                        )
                        if power_desc and not power_desc.startswith("powers."):
                            power_details.append(f"  {power_name}: {power_desc}")
                        else:
                            power_details.append(f"  {power_name}")
        if power_details:
            lines.append(t("combat.power_details", default="Powers:"))
            lines.extend(power_details)              
        # Relic descriptions
        relic_details = []
        if player.relics:
            for relic in player.relics:
                relic_id = relic.__class__.__name__
                if relic_id not in shown_relics:
                    shown_relics.add(relic_id)
                    relic_name = relic.local("name").resolve() if hasattr(relic, 'local') else relic.name
                    relic_desc = relic.local("description").resolve() if hasattr(relic, 'local') else ""
                    # Only add description if it exists and is not the raw key
                    if relic_desc and not relic_desc.startswith("relics."):
                        relic_details.append(f"  {relic_name}: {relic_desc}")
                    else:
                        relic_details.append(f"  {relic_name}")
        if relic_details:
            lines.append(t("combat.relic_details", default="Relics:"))
            lines.extend(relic_details)   
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
        lines.append("")
        
        ascension = getattr(gs, 'ascension_level', 0)
        
        # Group items by type
        cards = []
        relics = []
        potions = []
        
        for idx, shop_item in enumerate(room.items):
            if shop_item.purchased:
                continue
            if shop_item.item is None:
                continue
                
            final_price = shop_item.get_final_price_with_modifiers(ascension, gs)
            can_afford = gs.player.gold >= final_price
            
            if shop_item.item_type == "card":
                card_name = shop_item.item.info() if hasattr(shop_item.item, 'info') else str(shop_item.item.name)
                cards.append((idx, card_name, final_price, can_afford))
            elif shop_item.item_type == "relic":
                relic_name = shop_item.item.info() if hasattr(shop_item.item, 'info') else str(shop_item.item.name)
                relics.append((idx, relic_name, final_price, can_afford))
            elif shop_item.item_type == "potion":
                potion_name = shop_item.item.info() if hasattr(shop_item.item, 'info') else str(shop_item.item.name)
                potions.append((idx, potion_name, final_price, can_afford))
        
        # Display cards
        if cards:
            lines.append("[bold cyan]Cards:[/bold cyan]")
            for idx, name, price, can_afford in cards:
                if can_afford:
                    lines.append(f"  {name} - {price}g")
                else:
                    lines.append(f"  [dim]{name} - {price}g (can't afford)[/dim]")
            lines.append("")
        
        # Display relics
        if relics:
            lines.append("[bold magenta]Relics:[/bold magenta]")
            for idx, name, price, can_afford in relics:
                if can_afford:
                    lines.append(f"  {name} - {price}g")
                else:
                    lines.append(f"  [dim]{name} - {price}g (can't afford)[/dim]")
            lines.append("")
        
        # Display potions
        if potions:
            lines.append("[bold green]Potions:[/bold green]")
            for idx, name, price, can_afford in potions:
                if can_afford:
                    lines.append(f"  {name} - {price}g")
                else:
                    lines.append(f"  [dim]{name} - {price}g (can't afford)[/dim]")
            lines.append("")
        
        # Card removal service
        if not room.card_removal_used:
            from rooms.shop import _has_relic
            price = room.card_removal_price
            if _has_relic("SmilingMask", gs):
                price = 50
            elif _has_relic("MembershipCard", gs):
                price = int(price * 0.5)
            can_afford = gs.player.gold >= price
            lines.append("[bold yellow]Card Removal:[/bold yellow]")
            if can_afford:
                lines.append(f"  Remove a card - {price}g")
            else:
                lines.append(f"  [dim]Remove a card - {price}g (can't afford)[/dim]")
        
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
