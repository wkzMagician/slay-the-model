import random as rd
from typing import List, Optional

from engine.input_protocol import InputRequest, InputSubmission


class RuntimeContext:
    """Shared runtime helpers for participant assembly and input resolution."""

    def __init__(self, game_state=None, player=None, config=None, decision_engine=None):
        self.game_state = game_state
        self._player = player
        self._config = config
        self._decision_engine = decision_engine

    @property
    def player(self):
        if self._player is not None:
            return self._player
        return getattr(self.game_state, "player", None)

    @property
    def config(self):
        if self._config is not None:
            return self._config
        return getattr(self.game_state, "config", None)

    @property
    def decision_engine(self):
        if self._decision_engine is not None:
            return self._decision_engine
        return getattr(self.game_state, "decision_engine", None)

    @property
    def current_combat(self):
        return getattr(self.game_state, "current_combat", None)

    def message_participants(self, enemies=None, include_hand=False, hand=None) -> List:
        """Build the standard runtime participant list for message dispatch."""
        participants = []
        player = self.player
        if player is not None:
            participants.append(player)
            participants.extend(list(getattr(player, "relics", [])))
            participants.extend(list(getattr(player, "powers", [])))

        enemy_list = list(enemies or [])
        participants.extend(enemy_list)
        for enemy in enemy_list:
            participants.extend(list(getattr(enemy, "powers", [])))

        if include_hand:
            if hand is None and player is not None and getattr(player, "card_manager", None):
                hand = list(player.card_manager.get_pile("hand"))
            participants.extend(list(hand or []))

        return participants

    def resolve_input_request(self, request: InputRequest) -> InputSubmission:
        """Resolve one declarative input request based on the configured mode."""
        if request.request_type != "selection":
            return InputSubmission([])

        options = list(request.options or [])
        if not options:
            return InputSubmission([])

        if self.config.auto_select and len(options) == 1:
            return self._build_submission(options, [0])

        mode = self.config.mode
        if mode == "ai":
            selected_indices = self._resolve_ai_selection(request)
        elif mode == "debug":
            selected_indices = self._resolve_debug_selection(request)
        else:
            selected_indices = self._resolve_human_selection(request)

        return self._build_submission(options, selected_indices)

    def _augment_human_options(self, request: InputRequest) -> List:
        """Add human-only helper options such as the in-run menu."""
        options = list(request.options or [])
        show_menu = bool(self.config.human.get("show_menu_option", False))
        if not request.allow_menu or not show_menu:
            return options

        from actions.display import MenuAction
        from localization import LocalStr
        from utils.option import Option

        options.append(
            Option(
                name=LocalStr("ui.open_menu", default="Open the menu"),
                actions=[MenuAction(request)],
            )
        )
        return options

    def _resolve_human_selection(self, request: InputRequest) -> List[int]:
        """Resolve a selection request from CLI or TUI human input."""
        from localization import t
        from tui import get_app, is_tui_mode
        from tui.print_utils import tui_print

        options = self._augment_human_options(request)
        title = t(str(request.title), default=str(request.title)) if isinstance(request.title, str) else str(request.title or "")

        if is_tui_mode():
            app = get_app()
            if app:
                return app.request_selection_sync(
                    title=title,
                    options=options,
                    max_select=request.max_select,
                    must_select=request.must_select,
                )

        while True:
            if title:
                tui_print(title)

            for idx, option in enumerate(options, start=1):
                tui_print(f"  {idx}. {option.name}")

            if request.must_select:
                prompt = t("ui.select_prompt", default=f"Select (1-{len(options)}): ", count=len(options))
            else:
                prompt = t("ui.select_prompt", default=f"Select (0-{len(options)}): ", count=len(options))

            raw = input(prompt)
            parsed = self._parse_selection_input(
                raw_input=raw,
                option_count=len(options),
                max_select=request.max_select,
                must_select=request.must_select,
            )
            if parsed is not None:
                request.options = options
                return parsed

    def _resolve_ai_selection(self, request: InputRequest) -> List[int]:
        """Resolve a selection request through the configured AI decision engine."""
        from tui import get_app, is_tui_mode

        options = list(request.options or [])
        if not options:
            return []

        if self.decision_engine is None:
            return self._resolve_debug_selection(request)

        title = str(request.title or "")
        option_text = [str(option.name) for option in options]
        context = request.context or {}
        max_select = len(options) if request.max_select == -1 else request.max_select

        if is_tui_mode():
            app = get_app()
            if app and hasattr(self.decision_engine, "make_decision_with_streaming"):
                def streaming_callback(chunk_type, content):
                    panel = app.get_selection_panel()
                    if hasattr(panel, "append_streaming_content"):
                        panel.append_streaming_content(chunk_type, content)

                selected_indices, _thinking = self.decision_engine.make_decision_with_streaming(
                    title,
                    option_text,
                    context,
                    max_select,
                    streaming_callback=streaming_callback,
                )
                return selected_indices

        if hasattr(self.decision_engine, "make_decision_with_thinking"):
            selected_indices, _thinking = self.decision_engine.make_decision_with_thinking(
                title,
                option_text,
                context,
                max_select,
            )
            return selected_indices

        return self.decision_engine.make_decision(title, option_text, context, max_select)

    def _resolve_debug_selection(self, request: InputRequest) -> List[int]:
        """Resolve a request automatically in debug mode."""
        options = list(request.options or [])
        if not options:
            return []

        actual_max_select = len(options) if request.max_select == -1 else max(0, request.max_select)
        if actual_max_select == 0:
            return []

        select_type = self.config.get("debug.select_type", "random")
        if select_type == "first":
            return list(range(min(actual_max_select, len(options))))
        if select_type == "last":
            start = max(0, len(options) - actual_max_select)
            return list(range(start, len(options)))

        heuristic_selection = self._resolve_debug_selection_with_heuristics(
            options,
            actual_max_select,
        )
        if heuristic_selection is not None:
            return heuristic_selection

        sample_size = min(actual_max_select, len(options))
        return sorted(rd.sample(range(len(options)), sample_size))

    def _resolve_debug_selection_with_heuristics(
        self,
        options: List,
        actual_max_select: int,
    ) -> Optional[List[int]]:
        """Prefer progress-making actions in combat before falling back to randomness."""
        if actual_max_select != 1 or not self.current_combat:
            return None

        scored = []
        for idx, option in enumerate(options):
            score = self._score_debug_option(option)
            scored.append((score, idx))

        if not scored:
            return None

        best_score = max(score for score, _idx in scored)
        if best_score <= 0:
            return None

        best_indices = [idx for score, idx in scored if score == best_score]
        return [best_indices[0]]

    def _score_debug_option(self, option) -> int:
        """Heuristic score for debug auto-selection in combat."""
        from actions.combat import EndTurnAction, PlayCardAction, UsePotionAction
        from utils.types import CardType

        actions = list(getattr(option, "actions", []) or [])
        if not actions:
            return 0

        score = 1
        for action in actions:
            if isinstance(action, EndTurnAction):
                score = max(score, 5)
                continue

            if isinstance(action, PlayCardAction):
                card = getattr(action, "card", None)
                if getattr(card, "card_type", None) == CardType.ATTACK:
                    return 100
                score = max(score, 40)
                continue

            if isinstance(action, UsePotionAction):
                potion = getattr(action, "potion", None)
                potion_name = getattr(potion, "__class__", type("X", (), {})).__name__.lower()
                if any(token in potion_name for token in ("attack", "explosive", "fire", "poison", "fear")):
                    score = max(score, 70)
                else:
                    score = max(score, 20)

        return score

    def _parse_selection_input(
        self,
        raw_input: str,
        option_count: int,
        max_select: int,
        must_select: bool,
    ) -> Optional[List[int]]:
        """Parse and validate comma-separated human input into zero-based indices."""
        from localization import t
        from tui.print_utils import tui_print

        raw_input = (raw_input or "").strip()
        if not raw_input:
            tui_print(t("ui.invalid_input", default="Invalid input."))
            return None

        if not must_select and raw_input == "0":
            return []

        parts = [part.strip() for part in raw_input.split(",") if part.strip()]
        numbers: List[int] = []
        for part in parts:
            if not part.isdigit():
                tui_print(t("ui.invalid_input", default="Invalid input."))
                return None
            numbers.append(int(part))

        if 0 in numbers:
            tui_print(t("ui.stop_option_mixed", default="0 can only be entered by itself."))
            return None

        unique_numbers = list(dict.fromkeys(numbers))
        indices = [number - 1 for number in unique_numbers]

        for index in indices:
            if index < 0 or index >= option_count:
                tui_print(t("ui.invalid_option", default="Invalid option."))
                return None

        actual_max_select = option_count if max_select == -1 else max_select
        if len(indices) > actual_max_select:
            tui_print(
                t(
                    "ui.too_many_options",
                    default="Too many options selected (max {max_select}).",
                    max_select=actual_max_select,
                )
            )
            return None

        if must_select and len(indices) != actual_max_select:
            tui_print(
                t(
                    "ui.selection_count_mismatch",
                    default="Select exactly {count} option(s).",
                    count=actual_max_select,
                )
            )
            return None

        return indices

    def _build_submission(self, options: List, selected_indices: List[int]) -> InputSubmission:
        """Turn selected option indices into an actionable submission."""
        from actions.display import build_selected_options, show_selected_options

        if not selected_indices:
            if self.game_state is not None:
                self.game_state.last_select_idx = -1
            return InputSubmission([])

        if self.game_state is not None:
            self.game_state.last_select_idx = selected_indices[0]
        selected_options = build_selected_options(options, selected_indices)
        show_selected_options(selected_options)

        actions = []
        for idx in selected_indices:
            if 0 <= idx < len(options):
                actions.extend(options[idx].actions)
        return InputSubmission(actions)
