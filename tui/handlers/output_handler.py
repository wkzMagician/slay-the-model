# -*- coding: utf-8 -*-
"""
Output handler - manages the output panel for combat log and messages.
"""
from collections import deque
from typing import Optional


class OutputHandler:
    """Handles output panel content and message classification."""
    
    MAX_HISTORY = 1000
    
    def __init__(self, app):
        self._app = app
        self._history: deque = deque(maxlen=self.MAX_HISTORY)
    
    def add_message(self, message: str, msg_type: str = "ui"):
        """Add message to output panel with classification."""
        message = message.strip()
        if not message:
            return
        
        classified_type = self.classify_message(message) if msg_type == "ui" else msg_type
        
        self._history.append((message, classified_type))
        self._app.add_output(message, classified_type)
    
    def classify_message(self, text: str) -> str:
        """Classify message type based on content."""
        text_lower = text.lower()
        
        combat_keywords = [
            "damage", "heal", "block", "energy", "hp:", "attack", 
            "defend", "turn", "intent", "strike", "bash", "slam",
            " inflicted ", " dealt ", " gained "
        ]
        
        reward_keywords = [
            "gold", "relic", "potion", "card reward", "obtain", 
            "added to deck", "removed from deck"
        ]
        
        state_keywords = [
            "floor", "room", "map", "enter", "leave", "start", "end",
            "act", "combat", "boss", "elite"
        ]
        
        error_keywords = ["error", "exception", "failed", "invalid"]
        
        if any(kw in text_lower for kw in error_keywords):
            return "error"
        elif any(kw in text_lower for kw in combat_keywords):
            return "combat"
        elif any(kw in text_lower for kw in reward_keywords):
            return "reward"
        elif any(kw in text_lower for kw in state_keywords):
            return "state"
        
        return "ui"
    
    def get_history(self) -> list:
        """Get message history."""
        return list(self._history)
    
    def clear_history(self):
        """Clear message history."""
        self._history.clear()
    
    def format_combat_log(self, max_lines: int = 50) -> str:
        """Format recent combat log for display."""
        recent = list(self._history)[-max_lines:]
        lines = []
        for msg, msg_type in recent:
            prefix = {
                "combat": "⚔ ",
                "reward": "💰 ",
                "state": "📍 ",
                "error": "❌ ",
                "ui": "   "
            }.get(msg_type, "   ")
            lines.append(f"{prefix}{msg}")
        return "\n".join(lines)
