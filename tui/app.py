# -*- coding: utf-8 -*-
"""
Main TUI application using Textual.
Three-panel layout: Display (game state), Selection (choices), Output (log)
"""
import concurrent.futures
import re
from typing import Optional, List, Dict, Any, Callable

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, Container, VerticalScroll
from textual.widgets import Header, Footer, Static, RichLog, Button, SelectionList, Input
from textual.widget import Widget
from textual.reactive import reactive
from textual.screen import Screen
from rich.text import Text
from rich.panel import Panel
from rich.console import Console

from localization import resolve_text
from . import set_app, get_app
from utils.option import match_option_command


class DisplayPanel(Widget):
    """Left panel: Shows game state (player info + room content).
    
    Uses Widget base class instead of Static to properly support scrolling.
    The actual content is rendered via an inner Static widget.
    """
    
    panel_content: reactive[str] = reactive("")
    player_info: reactive[str] = reactive("")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def update_player_info(self, player, gs):
        """Update player info section."""
        hp_bar = self._make_hp_bar(player.hp, player.max_hp)
        energy_str = f"Energy: {player.energy}/{player.max_energy}"
        block_str = f"Block: {player.block}"
        gold_str = f"Gold: {player.gold}"
        floor_str = f"Floor: {gs.current_floor + 1}"
        
        relics_str = ""
        if player.relics:
            relic_names = [r.display_name() for r in player.relics[:5]]
            relics_str = f"Relics: {', '.join(relic_names)}"
            if len(player.relics) > 5:
                relics_str += f" (+{len(player.relics) - 5})"
        
        # Deck info
        # deck_str = f"Deck: {len(player.deck)} cards"
        
        self.player_info = (
            f"\n{hp_bar}\n{energy_str} | {block_str} | {gold_str} | {floor_str}\n{relics_str}"
        )
        self._refresh_display()
    
    def _make_hp_bar(self, hp: int, max_hp: int, width: int = 20) -> str:
        """Create an ASCII-safe HP bar visualization."""
        filled = int((hp / max_hp) * width) if max_hp > 0 else 0
        bar = "#" * filled + "." * (width - filled)
        return f"HP: [{bar}] {hp}/{max_hp}"
    
    def update_content(self, content: str):
        """Replace main content area."""
        self.panel_content = content or ""
        self._refresh_display()
    
    def _refresh_display(self):
        """Render combined player info + content."""
        lines = []
        if self.player_info:
            lines.append(self.player_info)
            lines.append("─" * 40)
        if self.panel_content:
            lines.append(self.panel_content)
        # Update the inner Static widget, not self
        try:
            content_widget = self.query_one("#display-content", Static)
            content_widget.update("\n".join(lines))
        except Exception:
            pass  # Widget not yet mounted
    
    def compose(self) -> ComposeResult:
        # markup=False prevents bracket interpretation issues
        yield Static("", id="display-content", markup=False)


class SelectionPanel(Widget):
    """Middle panel: Shows current selection options.
    
    Uses Widget base class instead of Static to properly support scrolling.
    The actual content is rendered via inner Static widget.
    """
    
    options: reactive[List[Any]] = reactive([])
    title: reactive[str] = reactive("")
    selected_callback: Optional[Callable[[Any], None]] = None
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._options_data: List[Any] = []
        self._selection_future: Optional[concurrent.futures.Future[list[int]]] = None
        self._max_select = 1
        self._must_select = True
        self._is_ai_mode = False  # Track if running in AI mode
        # Streaming content buffers
        self._thinking_buffer: str = ""
        self._answer_buffer: str = ""
        self._is_streaming: bool = False
    
    def set_ai_mode(self, is_ai: bool):
        """Set whether the app is running in AI mode."""
        self._is_ai_mode = is_ai
        # Update input visibility
        try:
            input_widget = self.query_one("#selection-input", Input)
            input_widget.set_class(is_ai, "hidden")
        except Exception:
            pass
    
    def compose(self) -> ComposeResult:
        yield Static("[dim]Waiting...[/dim]", id="selection-content")  # Needs markup for colors
        yield Input(placeholder="Enter selection", id="selection-input")
    
    def set_selection(
        self,
        title: str,
        options: List[Any],
        callback: Optional[Callable[[Any], None]] = None,
        max_select: int = 1,
        must_select: bool = True,
        future: Optional[concurrent.futures.Future[list[int]]] = None,
    ):
        """Set current selection."""
        self.title = title
        self._options_data = options
        self.selected_callback = callback
        self._max_select = max_select
        self._must_select = must_select
        self._selection_future = future
        self._refresh_display()
        self.query_one("#selection-input", Input).focus()

    def _build_selection_lines(
        self,
        title: str,
        options: List[Any],
        max_select: int,
        must_select: bool,
    ) -> List[str]:
        lines = []
        if title:
            lines.append(f"[bold]{title}[/bold]")
            lines.append("")

        for i, opt in enumerate(options):
            name = resolve_text(opt.name) if hasattr(opt, "name") else resolve_text(opt)
            lines.append(f"  [cyan]{i + 1}.[/cyan] {name}")
            detail = resolve_text(getattr(opt, "detail", "")) if getattr(opt, "detail", None) else ""
            if detail:
                lines.append(f"      [dim]{detail}[/dim]")

        lines.append("")
        if must_select:
            required = len(options) if max_select == -1 else max_select
            lines.append(
                f"[dim]Enter {required} number(s), comma-separated (e.g. 1,3)[/dim]"
            )
        else:
            actual_max_select = len(options) if max_select == -1 else max_select
            lines.append(
                f"[dim]Enter up to {actual_max_select} number(s), comma-separated. Enter 0 to stop.[/dim]"
            )
        return lines
    
    def _refresh_display(self):
        """Render selection options."""
        lines = self._build_selection_lines(
            title=self.title,
            options=self._options_data,
            max_select=self._max_select,
            must_select=self._must_select,
        )
        self.query_one("#selection-content", Static).update("\n".join(lines))
    
    def select_by_index(self, idx: int) -> bool:
        """Select option by index."""
        if 0 <= idx < len(self._options_data):
            self._resolve_selection([idx])
            return True
        return False
    
    def on_input_submitted(self, event: Input.Submitted):
        """Handle input submit for single and multi-select."""
        raw_value = event.value.strip()
        parsed_indices = self._parse_indices(raw_value)
        if parsed_indices is None:
            event.input.value = ""
            return
        self._resolve_selection(parsed_indices)
    
    def _parse_indices(self, raw_value: str) -> Optional[List[int]]:
        """Parse comma-separated option numbers into zero-based indices."""
        command_match = match_option_command(raw_value, self._options_data)
        if command_match is not None:
            return command_match

        if not raw_value:
            self._show_validation_error("Input cannot be empty.")
            return None
        
        if not self._must_select and raw_value == "0":
            return []
        
        parts = [part.strip() for part in raw_value.split(",") if part.strip()]
        if not parts:
            self._show_validation_error("Invalid input format.")
            return None
        
        numbers: List[int] = []
        for part in parts:
            if not part.isdigit():
                self._show_validation_error("Use comma-separated numbers only.")
                return None
            value = int(part)
            if value == 0:
                self._show_validation_error("0 can only be entered alone to stop selection.")
                return None
            numbers.append(value)
        
        unique_numbers = list(dict.fromkeys(numbers))
        indices = [num - 1 for num in unique_numbers]
        
        for idx in indices:
            if idx < 0 or idx >= len(self._options_data):
                self._show_validation_error(f"Invalid option number: {idx + 1}")
                return None
        
        if self._max_select != -1 and len(indices) > self._max_select:
            self._show_validation_error(
                f"Too many selections (max {self._max_select})."
            )
            return None
        
        if self._must_select:
            required = len(self._options_data) if self._max_select == -1 else self._max_select
            if len(indices) != required:
                self._show_validation_error(
                    f"Select exactly {required} option(s)."
                )
                return None
        
        return indices
    
    def _resolve_selection(self, indices: List[int]):
        """Resolve callbacks/future with selected indices."""
        if self._selection_future and not self._selection_future.done():
            self._selection_future.set_result(indices)
        elif self.selected_callback:
            if len(indices) == 1:
                self.selected_callback(indices[0])
            else:
                self.selected_callback(indices)
        self.clear()
    
    def _show_validation_error(self, message: str):
        """Render validation error below selection instructions."""
        # Re-build display with error appended (Static.renderable doesn't exist in Textual 8.0)
        lines = self._build_selection_lines(
            title=self.title,
            options=self._options_data,
            max_select=self._max_select,
            must_select=self._must_select,
        )
        lines.append(f"[red]{message}[/red]")
        self.query_one("#selection-content", Static).update("\n".join(lines))




    
    def show_thinking(self, message: str):
        """Show AI thinking message in selection panel while preserving title and options.
        
        Also initializes streaming buffers for real-time content display.
        """
        # Initialize streaming buffers
        self._thinking_buffer = ""
        self._answer_buffer = ""
        self._is_streaming = True
        
        self._refresh_streaming_display(message)
    
    def start_streaming(self):
        """Initialize streaming mode without a message."""
        self._thinking_buffer = ""
        self._answer_buffer = ""
        self._is_streaming = True
        self._refresh_streaming_display("")
    
    def update_streaming_content(self, chunk_type: str, content: str):
        """Update AI streaming content in real-time.
        
        Args:
            chunk_type: "thinking" or "answer"
            content: Current chunk content (incremental)
        """
        if not self._is_streaming:
            self.start_streaming()
        
        if chunk_type == "thinking":
            self._thinking_buffer += content
        elif chunk_type == "answer":
            self._answer_buffer += content
        
        self._refresh_streaming_display()
    
    def _refresh_streaming_display(self, initial_message: str = ""):
        """Render selection panel with streaming content.
        
        Display format:
        - Title
        - Options
        - AI thinking content (if any)
        - AI answer content (if any)
        - Waiting message
        """
        lines = []
        
        # Title
        if self.title:
            lines.append(f"[bold]{self.title}[/bold]")
            lines.append("")
        
        # Options
        for i, opt in enumerate(self._options_data):
            name = str(opt.name) if hasattr(opt, 'name') else str(opt)
            lines.append(f"  [cyan]{i + 1}.[/cyan] {name}")
        
        lines.append("")
        
        # AI thinking content
        if self._thinking_buffer:
            lines.append("[dim]── AI 思考过程 ──[/dim]")
            # Truncate if too long (keep last ~500 chars for display)
            thinking_display = self._thinking_buffer
            if len(thinking_display) > 500:
                thinking_display = "...(省略前面内容)..." + thinking_display[-450:]
            # Escape brackets to prevent markup interpretation
            thinking_escaped = thinking_display.replace("[", "\\[")
            lines.append(f"[yellow]{thinking_escaped}[/yellow]")
            lines.append("")
        
        # AI answer content
        if self._answer_buffer:
            lines.append("[dim]── AI 回答 ──[/dim]")
            answer_display = self._answer_buffer
            if len(answer_display) > 200:
                answer_display = answer_display[-180:] + "..."
            answer_escaped = answer_display.replace("[", "\\[")
            lines.append(f"[green]{answer_escaped}[/green]")
            lines.append("")
        
        # Initial message (if no streaming content yet)
        if initial_message and not self._thinking_buffer and not self._answer_buffer:
            lines.append(f"[yellow]{initial_message}[/yellow]")
            lines.append("")
        
        # Waiting message
        if self._must_select:
            required = len(self._options_data) if self._max_select == -1 else self._max_select
            lines.append(
                f"[dim]Waiting for AI... ({required} selection(s) needed)[/dim]"
            )
        else:
            max_select = len(self._options_data) if self._max_select == -1 else self._max_select
            lines.append(
                f"[dim]Waiting for AI... (up to {max_select} selection(s))[/dim]"
            )
        
        self.query_one("#selection-content", Static).update("\n".join(lines))
    
    def stop_streaming(self):
        """Stop streaming mode."""
        self._is_streaming = False
    
    def clear(self):
        """Clear selection panel."""
        self.title = ""
        self._options_data = []
        self.selected_callback = None
        self._selection_future = None
        self.query_one("#selection-content", Static).update("[dim]Waiting...[/dim]")
        selection_input = self.query_one("#selection-input", Input)
        selection_input.value = ""
        selection_input.placeholder = "Enter selection"



class OutputPanel(RichLog):
    """Right panel: Scrollable combat log and messages."""
    
    MAX_LINES = 500
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, max_lines=self.MAX_LINES, wrap=True, highlight=True)
    
    def add_combat_message(self, message: str):
        """Add combat-related message."""
        self.write(Text(message, style="green"))
    
    def add_state_message(self, message: str):
        """Add state change message."""
        self.write(Text(message, style="yellow"))
    
    def add_reward_message(self, message: str):
        """Add reward message."""
        self.write(Text(message, style="magenta"))
    
    def add_debug_message(self, message: str):
        """Add debug message."""
        self.write(Text(message, style="dim"))
    
    def add_error_message(self, message: str):
        """Add error message."""
        self.write(Text(message, style="red bold"))


class MainScreen(Screen):
    """Main game screen with three panels."""
    
    CSS_PATH = "styles.css"
    
    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="main-container"):
            with VerticalScroll(id="display-panel-container"):
                yield DisplayPanel(id="display-panel")
            with VerticalScroll(id="selection-panel-container"):
                yield SelectionPanel(id="selection-panel")
            with VerticalScroll(id="output-panel-container"):
                yield OutputPanel(id="output-panel")
        yield Footer()
    
    def on_key(self, event):
        """Handle keyboard input for selection."""
        if event.key.isdigit():
            idx = int(event.key) - 1
            selection_panel = self.query_one("#selection-panel", SelectionPanel)
            selection_panel.select_by_index(idx)
    
    def on_mount(self):
        """Start game after widgets are fully mounted."""
        _t = 0.1
        self.set_timer(_t, self._start_game)
    
    def _start_game(self):
        """Actually start the game (called after delay)."""
        self.app.start_game()


class SlayTheModelApp(App):
    """Main TUI application for Slay the Model."""
    
    CSS_PATH = "styles.css"
    SCREENS = {"main": MainScreen}
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("d", "toggle_dark", "Toggle Dark"),
    ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._is_ai_mode = False  # Track if running in AI mode
    
    def on_mount(self):
        """Set up app on mount."""
        set_app(self)
        self.push_screen("main")
        # Apply AI mode if it was set before screen was ready
        if self._is_ai_mode:
            self.call_later(self._apply_ai_mode)
    
    def set_ai_mode(self, is_ai: bool):
        """Set whether the app is running in AI mode."""
        self._is_ai_mode = is_ai
    
    def _apply_ai_mode(self):
        """Apply AI mode to selection panel after screen is ready."""
        try:
            panel = self.get_selection_panel()
            panel.set_ai_mode(self._is_ai_mode)
        except Exception:
            pass
    
    def start_game(self):
        """Start game loop in worker thread. Called by MainScreen when ready."""
        self.run_worker(self._run_game, thread=True, exclusive=True)

    def _run_game(self):
        """Run blocking game flow in worker thread."""
        from engine.game_flow import GameFlow
        from engine.game_state import game_state
        import cards.ironclad  # noqa: F401
        import potions  # noqa: F401
        from powers import definitions  # noqa: F401
        import relics  # noqa: F401

        try:
            GameFlow().start_game(game_state)
            self._show_game_over_message()
        finally:
            # Don't auto-exit - let user close window manually
            pass
    
    def _show_game_over_message(self):
        """Show game over/victory message and wait for user."""
        from localization import t
        from engine.game_state import game_state
        
        # Check game state to determine message
        # Game will have completed by now, check if player won/lost/exited
        message = t('ui.game_finished', default='Game Finished')
        sub_message = t('ui.press_to_exit', default='Press [q] or [Ctrl+C] to exit')
        
        # Show message in display panel
        self.update_display_content(f"[bold green]{message}[/bold green]\n\n[yellow]{sub_message}[/yellow]")
        
        # Log to output panel as well
        self.add_output(f"\n{message}", "state")
        self.add_output(sub_message, "ui")
    
    def on_unmount(self):
        """Clean up on unmount."""
        set_app(None)
    
    def get_display_panel(self) -> DisplayPanel:
        """Get display panel widget."""
        return self.screen.query_one("#display-panel", DisplayPanel)


    
    def get_selection_panel(self) -> SelectionPanel:
        """Get selection panel widget."""
        return self.screen.query_one("#selection-panel", SelectionPanel)


    
    def get_output_panel(self) -> OutputPanel:
        """Get output panel widget."""
        return self.screen.query_one("#output-panel", OutputPanel)


    
    def update_player_info(self, player, gs):
        """Update player info in display panel."""
        self.get_display_panel().update_player_info(player, gs)
    
    def update_display_content(self, content: str):
        """Update display panel content."""
        self.get_display_panel().update_content(content)
    
    def show_selection(self, title: str, options: List[Any]) -> int:
        """Show selection and wait for input. Returns selected index."""
        self.get_selection_panel().set_selection(title, options)
        return 0

    def request_selection_sync(
        self,
        title: str,
        options: List[Any],
        max_select: int,
        must_select: bool,
    ) -> List[int]:
        """Bridge blocking game thread to async TUI selection."""
        future: concurrent.futures.Future[list[int]] = concurrent.futures.Future()
        request = {
            "title": title,
            "options": options,
            "max_select": max_select,
            "must_select": must_select,
        }
        self.call_from_thread(self._present_selection, request, future)
        return future.result()

    def _present_selection(
        self,
        request: Dict[str, Any],
        future: concurrent.futures.Future[list[int]],
    ):
        """Present selection request in UI thread and store pending future."""
        self.get_selection_panel().set_selection(
            request["title"],
            request["options"],
            max_select=request["max_select"],
            must_select=request["must_select"],
            future=future,
        )
    
    def add_output(self, message: str, msg_type: str = "combat"):
        """Add message to output panel."""
        if self._should_suppress_output_message(message, msg_type):
            return

        panel = self.get_output_panel()
        if msg_type == "combat":
            panel.add_combat_message(message)
        elif msg_type == "map":
            panel.add_state_message(message)
        elif msg_type == "state":
            panel.add_state_message(message)
        elif msg_type == "reward":
            panel.add_reward_message(message)
        elif msg_type == "debug":
            panel.add_debug_message(message)
        elif msg_type == "error":
            panel.add_error_message(message)
        else:
            panel.write(message)
    
    def capture_print(self, text: str):
        """Capture print output and route to panels."""
        text = text.strip()
        if not text:
            return

        msg_type = self._classify_message(text)
        self.call_from_thread(self.add_output, text, msg_type)
    
    def _classify_message(self, text: str) -> str:
        """Classify message type for routing."""
        text_lower = text.lower()
        combat_keywords = ["damage", "heal", "block", "energy", "hp:", "attack", "defend", "turn", "intent"]
        map_keywords = ["map", "path", "route", "node", "地图", "路线", "节点"]
        reward_keywords = ["gold", "relic", "potion", "card", "reward", "obtain"]
        state_keywords = ["floor", "room", "map", "enter", "leave", "start", "end"]

        if any(kw in text_lower for kw in combat_keywords):
            return "combat"
        elif any(kw in text_lower for kw in map_keywords):
            return "map"
        elif any(kw in text_lower for kw in reward_keywords):
            return "reward"
        elif any(kw in text_lower for kw in state_keywords):
            return "state"
        return "ui"

    def _should_suppress_output_message(self, message: str, msg_type: str) -> bool:
        """Filter high-noise map/combat state dumps from output panel."""
        text = (message or "").strip()
        if not text:
            return True

        text_lower = text.lower()

        # Always keep important channels.
        if msg_type in ("error", "reward", "debug"):
            return False

        # # Suppress map ASCII dumps and map debug lines (map is shown in display panel).
        # if text.startswith("MAP VIEW - Act"):
        #     return True
        # if text.startswith("Legend:") or text.startswith("Connections:"):
        #     return True
        # if text.startswith("DEBUG: self.act_id=") or text.startswith("DEBUG: self._act_floor_counts="):
        #     return True
        # if text.startswith("DEBUG: current_floor="):
        #     return True
        # if re.match(r"^Floor\s+\d+:", text):
        #     return True
        # if set(text).issubset(set(" /|\\")) and text:
        #     return True

        # # Suppress combat state snapshot spam (now shown in display panel).
        # if text.startswith("--- Combat Status ---"):
        #     return True
        # if text.startswith("=== Player Turn") or text.startswith("=== Enemy Turn"):
        #     return True
        # if text.startswith("Hand ("):
        #     return True
        # if text.startswith("Draw Pile") or text.startswith("Discard Pile"):
        #     return True
        # if text.startswith("=== Enemies ==="):
        #     return True
        # if text.startswith("Powers:"):
        #     return True
        # if re.match(r"^\s*\[\d+\]\s+", text):
        #     return True
        # if text_lower.startswith("hp:") and "/" in text and "damage" not in text_lower:
        #     return True
        # if text_lower.startswith("block:"):
        #     return True
        # if text_lower.startswith("energy:") and "/" in text:
        #     return True
        # if text_lower.startswith("intention:"):
        #     return True

        return False
    
    def clear_game_selection(self):
        """Clear selection panel."""
        self.get_selection_panel().clear()
