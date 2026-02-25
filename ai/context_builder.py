# -*- coding: utf-8 -*-
"""
AI Context Builder - Builds comprehensive game state context for LLM decision making.

This module constructs a detailed, human-readable context string that includes:
- Player status (HP, energy, gold, floor, block)
- Relics with full descriptions
- Powers on player with full descriptions
- Combat status (enemies, hand cards, deck piles)
- All card/relic/power descriptions are included (AI has no prior knowledge)
"""
from typing import TYPE_CHECKING

from localization import t

if TYPE_CHECKING:
    from engine.game_state import GameState
    from engine.combat import Combat


class AIContextBuilder:
    """Builds comprehensive game state context for AI decision making.
    
    The output is formatted as Markdown for optimal LLM readability.
    Reuses the structure from DisplayHandler but enhances with full descriptions.
    """
    
    @staticmethod
    def build_context(gs: 'GameState') -> str:
        """Build complete context string for AI decision making.
        
        Args:
            gs: GameState instance
            
        Returns:
            Markdown-formatted string containing game state information
        """
        sections = []
        
        # 1. Player base status
        sections.append(AIContextBuilder._build_player_status(gs))
        
        # 2. Relics with full descriptions
        if gs.player.relics:
            sections.append(AIContextBuilder._build_relics_info(gs))
        
        # 3. Powers on player with full descriptions
        if gs.player.powers:
            sections.append(AIContextBuilder._build_player_powers(gs))
        
        # 4. Combat status (if in combat)
        if gs.current_combat:
            sections.append(AIContextBuilder._build_combat_status(gs))
        
        # 5. Non-combat room info (if applicable)
        elif gs.current_room:
            sections.append(AIContextBuilder._build_room_info(gs))
        
        return "\n\n".join(filter(None, sections))
    
    @staticmethod
    def _build_player_status(gs: 'GameState') -> str:
        """Build player status section."""
        player = gs.player
        lines = [
            f"# {t('ai_context.player_status')}",
            f"- {t('ai_context.hp')}: {player.hp}/{player.max_hp} | {t('ai_context.energy')}: {player.energy}/{player.max_energy} | {t('ai_context.gold')}: {player.gold}",
            f"- {t('ai_context.floor')}: {gs.current_floor + 1} | {t('ai_context.block')}: {player.block}",
            f"- {t('ai_context.deck')}: {len(player.deck)} {t('ai_context.cards_total')}",
        ]
        
        # Max energy (if different from base)
        if player.max_energy != 3:
            lines.append(f"- {t('ai_context.max_energy')}: {player.max_energy}")
        
        return "\n".join(lines)
    
    @staticmethod
    def _build_relics_info(gs: 'GameState') -> str:
        """Build relics section with full descriptions."""
        player = gs.player
        lines = [f"## {t('ai_context.relics')} ({len(player.relics)})"]
        
        for i, relic in enumerate(player.relics, 1):
            name = relic.local("name").resolve()
            desc = relic.local("description").resolve()
            # Clean up description formatting
            desc = desc.replace("{amount}", str(getattr(relic, 'amount', '')))
            lines.append(f"{i}. **{name}**: {desc}")
        
        return "\n".join(lines)
    
    @staticmethod
    def _build_player_powers(gs: 'GameState') -> str:
        """Build player powers section with full descriptions."""
        player = gs.player
        lines = [f"## {t('ai_context.powers_on_you')}"]
        
        for i, power in enumerate(player.powers, 1):
            name = power.local("name").resolve()
            desc = power.local("description").resolve()
            # Format amount
            amt_str = f" x{power.amount}" if power.amount > 0 else ""
            # Clean up description
            desc = desc.replace("{amount}", str(power.amount))
            lines.append(f"{i}. **{name}{amt_str}**: {desc}")
        
        return "\n".join(lines)
    
    @staticmethod
    def _build_combat_status(gs: 'GameState') -> str:
        """Build combat status section with full information."""
        combat = gs.current_combat
        player = gs.player
        
        # Get card piles
        hand = list(player.card_manager.get_pile("hand"))
        draw_pile = list(player.card_manager.get_pile("draw_pile"))
        discard = list(player.card_manager.get_pile("discard_pile"))
        exhaust = list(player.card_manager.get_pile("exhaust_pile"))
        
        sections = [f"# {t('ai_context.combat_status')}"]
        
        # Enemies with full info
        alive_enemies = [e for e in combat.enemies if not e.is_dead()]
        
        # Build enemy section
        enemy_lines = [f"## {t('ai_context.enemies')}"]
        if not alive_enemies:
            enemy_lines.append(t('ai_context.no_enemies'))
        else:
            for i, enemy in enumerate(alive_enemies, 1):
                # Enemy name
                if hasattr(enemy, 'local'):
                    name = enemy.local("name").resolve()
                else:
                    name = getattr(enemy, 'name', str(enemy.__class__.__name__))
                
                # HP and Block
                hp_str = f"{t('ai_context.hp')}: {enemy.hp}/{enemy.max_hp}"
                block_str = f"{t('ai_context.block')}: {enemy.block}" if enemy.block > 0 else f"{t('ai_context.block')}: 0"
                
                enemy_lines.append(f"{i}. **{name}** - {hp_str} | {block_str}")
                
                # Intent
                if hasattr(enemy, 'current_intention') and enemy.current_intention:
                    intent = enemy.current_intention
                    intent_str = AIContextBuilder._format_intent(intent)
                    enemy_lines.append(f"   - {t('ai_context.intent')}: {intent_str}")
                
                # Enemy powers with descriptions
                if enemy.powers:
                    for power in enemy.powers:
                        pname = power.local("name").resolve()
                        pdesc = power.local("description").resolve()
                        pdesc = pdesc.replace("{amount}", str(power.amount))
                        pamt = f" x{power.amount}" if power.amount > 0 else ""
                        enemy_lines.append(f"   - {t('ai_context.power')}: **{pname}{pamt}**: {pdesc}")
        
        sections.append("\n".join(enemy_lines))
        
        # Hand cards with full info
        hand_lines = [f"## {t('ai_context.hand')} ({len(hand)} {t('ai_context.cards')})"]
        
        for i, card in enumerate(hand, 1):
            card_info = AIContextBuilder._format_card_info(card)
            hand_lines.append(f"{i}. {card_info}")
        
        sections.append("\n".join(hand_lines))
        
        # Draw pile (names only, it's shuffled)
        draw_names = [AIContextBuilder._get_card_name(c) for c in draw_pile]
        draw_line = f"{t('combat.draw_pile')} ({len(draw_pile)}): {', '.join(draw_names) if draw_names else t('ui.empty')}"
        
        # Discard pile
        discard_names = [AIContextBuilder._get_card_name(c) for c in discard]
        discard_line = f"{t('combat.discard_pile')} ({len(discard)}): {', '.join(discard_names) if discard_names else t('ui.empty')}"
        
        # Exhaust pile
        exhaust_names = [AIContextBuilder._get_card_name(c) for c in exhaust]
        exhaust_line = f"{t('combat.exhaust_pile', default='Exhaust Pile')} ({len(exhaust)}): {', '.join(exhaust_names) if exhaust_names else t('ui.empty')}"
        
        sections.append(f"## {t('ai_context.deck_status')}\n" + "\n".join([draw_line, discard_line, exhaust_line]))
        
        return "\n\n".join(sections)
    
    @staticmethod
    def _build_room_info(gs: 'GameState') -> str:
        """Build non-combat room information."""
        room = gs.current_room
        if not room:
            return ""
        
        room_type = type(room).__name__
        lines = [f"# {t('ai_context.current_room')}: {room_type}"]
        
        # Add room-specific info based on type
        if room_type == "ShopRoom":
            lines.append(AIContextBuilder._build_shop_info(room))
        elif room_type == "RestRoom":
            lines.append(t('ai_context.rest_options'))
        
        return "\n".join(lines)
    
    @staticmethod
    def _build_shop_info(room) -> str:
        """Build shop item information."""
        lines = [f"## {t('ai_context.shop_items')}"]
        
        # Cards for sale
        if hasattr(room, 'cards') and room.cards:
            lines.append(f"### {t('ai_context.cards_for_sale')}:")
            for i, card in enumerate(room.cards, 1):
                price = getattr(card, 'price', '?')
                card_info = AIContextBuilder._format_card_info(card)
                lines.append(f"{i}. {card_info} - {t('ai_context.price')}: {price}g")
        
        # Relics for sale
        if hasattr(room, 'relics') and room.relics:
            lines.append(f"### {t('ai_context.relics_for_sale')}:")
            for i, relic in enumerate(room.relics, 1):
                price = getattr(relic, 'price', '?')
                name = relic.local("name").resolve()
                desc = relic.local("description").resolve()
                lines.append(f"{i}. **{name}**: {desc} - {t('ai_context.price')}: {price}g")
        
        # Potions for sale
        if hasattr(room, 'potions') and room.potions:
            lines.append(f"### {t('ai_context.potions_for_sale')}:")
            for i, potion in enumerate(room.potions, 1):
                price = getattr(potion, 'price', '?')
                name = potion.local("name").resolve()
                desc = potion.local("description").resolve()
                lines.append(f"{i}. **{name}**: {desc} - {t('ai_context.price')}: {price}g")
        
        # Card removal service
        lines.append(f"### {t('ai_context.services')}:")
        lines.append(f"- {t('ai_context.remove_card_service')}")
        
        return "\n".join(lines)
    
    @staticmethod
    def _format_card_info(card) -> str:
        """Format a card with full information."""
        # Name
        if hasattr(card, 'display_name'):
            name = card.display_name.resolve()
        elif hasattr(card, 'local'):
            name = card.local("name").resolve()
        else:
            name = card.__class__.__name__
        
        # Cost
        cost = card.cost if hasattr(card, 'cost') and card.cost is not None else 0
        if cost < 0:
            cost_str = "X"
        elif cost == -1:
            cost_str = "X"
        else:
            cost_str = str(cost)
        
        # Type - localize card type
        if hasattr(card, 'card_type'):
            ctype_val = card.card_type.value if hasattr(card.card_type, 'value') else str(card.card_type)
            ctype = t(f'card_type.{ctype_val.lower()}', default=ctype_val)
        else:
            ctype = t('ui.unknown', default='Unknown')
        
        # Stats (damage, block)
        stats = []
        if hasattr(card, 'damage') and card.damage and card.damage > 0:
            stats.append(f"{t('ai_context.dmg')}:{card.damage}")
        if hasattr(card, 'block') and card.block and card.block > 0:
            stats.append(f"{t('ai_context.blk')}:{card.block}")
        stats_str = f" ({', '.join(stats)})" if stats else ""
        
        # Description
        if hasattr(card, 'local'):
            desc = card.local("description").resolve()
            # Format variables in description
            if hasattr(card, 'damage') and card.damage:
                desc = desc.replace("{damage}", str(card.damage))
            if hasattr(card, 'block') and card.block:
                desc = desc.replace("{block}", str(card.block))
            # Handle magic.XXX placeholders - need to access _magic dict
            if hasattr(card, '_magic') and card._magic:
                for magic_key, magic_val in card._magic.items():
                    desc = desc.replace(f"{{magic.{magic_key}}}", str(magic_val))
        else:
            desc = ""
        # Build formatted string
        result = f"**[{cost_str}] {name} [{ctype}]{stats_str}**"
        if desc:
            result += f"\n   {desc}"
        
        return result
    
    @staticmethod
    def _get_card_name(card) -> str:
        """Get just the name of a card."""
        if hasattr(card, 'display_name'):
            return card.display_name.resolve()
        elif hasattr(card, 'local'):
            return card.local("name").resolve()
        else:
            return card.__class__.__name__
    
    @staticmethod
    def _format_intent(intent) -> str:
        """Format enemy intent for readability."""
        if not intent:
            return t('ui.unknown', default='Unknown')
        
        # First try to get the description from the intent object
        if hasattr(intent, 'description'):
            desc = intent.description
            if hasattr(desc, 'resolve'):
                return desc.resolve()
            return str(desc)
        
        # Fallback: try to get intent name
        if hasattr(intent, 'name'):
            return str(intent.name)
        
        # Last resort: return Unknown
        return "Unknown"
