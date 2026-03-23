# -*- coding: utf-8 -*-
"""
Selection handler - manages the selection panel for input-request integration.
"""
from typing import List, Optional, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from actions.display import InputRequestAction
    from utils.option import Option


class SelectionHandler:
    """Handles selection panel interactions."""
    
    def __init__(self, app):
        self._app = app
        self._current_action: Optional['InputRequestAction'] = None
        self._pending_result = None
    
    def show_selection(self, select_action: 'InputRequestAction') -> int:
        """
        Display selection options from InputRequestAction.
        Returns selected index (called synchronously, actual selection happens async).
        """
        self._current_action = select_action
        
        title = str(select_action.request.title) if select_action.request.title else "Choose:"
        options = select_action.request.options
        
        self._app.show_selection(title, options)
        
        return 0
    
    def handle_input(self, key: str) -> bool:
        """Handle keyboard input. Returns True if input was consumed."""
        if key.isdigit():
            idx = int(key) - 1
            return self.select_by_index(idx)
        return False
    
    def select_by_index(self, idx: int) -> bool:
        """Select option by index. Returns True if valid selection."""
        if self._current_action and 0 <= idx < len(self._current_action.request.options):
            self._pending_result = idx
            return True
        return False
    
    def get_result(self) -> Optional[int]:
        """Get pending selection result."""
        return self._pending_result
    
    def clear(self):
        """Clear selection state."""
        self._current_action = None
        self._pending_result = None
        self._app.clear_selection()
