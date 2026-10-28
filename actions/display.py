# -*- coding: utf-8 -*-
"""Display actions and declarative input requests."""
from engine.runtime_api import add_action, add_actions, publish_message, request_input, set_terminal_state
from typing import Dict, List, Optional

from actions.base import Action, LambdaAction
from engine.input_protocol import InputRequest
from engine.runtime_events import emit_lines, emit_text
from engine.runtime_presenter import flush_runtime_events
from localization import BaseLocalStr, LocalStr, resolve_text, t
from utils.option import Option, selection_error
from utils.registry import register
from utils.result_types import GameTerminalState


def _resolve_title(title: object) -> str:
    return resolve_text(title)


def build_selected_options(
    options: List[Option],
    selected_indices: List[int],
) -> Dict[int, Option]:
    """Build a stable selection map keyed by original option index."""
    if selection_error(options, selected_indices) is not None:
        return {}
    return {idx: options[idx] for idx in selected_indices}


def show_selected_options(selected_options: Dict[int, Option]):
    """Emit the selected options through the runtime event layer."""
    if not selected_options:
        return

    lines = [f"\n{t('ui.selected', default='Selected:')}"]
    for idx, option in selected_options.items():
        lines.append(f"  {idx + 1}. {resolve_text(option.name)}")
        if option.detail:
            lines.append(f"     {resolve_text(option.detail)}")

    emit_lines(lines)
    flush_runtime_events()


@register("action")
class DisplayTextAction(Action):
    """Display localized text in CLI or TUI output."""

    def __init__(self, text_key: str = "", **fmt):
        self.text_key = text_key
        self.fmt = fmt

    def execute(self) -> None:
        fallback = self.fmt.get("default", self.text_key)
        text = t(
            self.text_key,
            default=fallback,
            **{k: v for k, v in self.fmt.items() if k != "default"},
        )
        emit_text(text, end="")
        flush_runtime_events()


@register("action")
class InputRequestAction(Action):
    """Action wrapper that pauses execution and asks the driver for input."""

    def __init__(
        self,
        title: Optional[BaseLocalStr] = None,
        options: Optional[List[Option]] = None,
        max_select: int = 1,
        must_select: bool = True,
        context: Optional[Dict] = None,
        request_type: str = "selection",
        allow_menu: bool = True,
    ):
        self.request = InputRequest(
            title=title,
            options=options if options is not None else [],
            max_select=max_select,
            must_select=must_select,
            context=context or {},
            request_type=request_type,
            allow_menu=allow_menu,
        )
        self.title = self.request.title
        self.options = self.request.options
        self.max_select = self.request.max_select
        self.must_select = self.request.must_select
        self.context = self.request.context

    def execute(self) -> None:
        from engine.game_state import game_state

        if not self.request.options and self.request.request_type == "selection":
            return
        request_input(self.request)

    def _build_selected_options(self, options, selected_indices):
        return build_selected_options(options, selected_indices)

    def show_choose(self, selected_options):
        show_selected_options(selected_options)


@register("action")
class ResumeInputRequestAction(Action):
    """Re-open a previous input request."""

    def __init__(self, request: InputRequest):
        self.request = request

    def execute(self) -> None:
        from engine.game_state import game_state

        request_input(self.request)


@register("action")
class MenuAction(Action):
    """Open the in-run menu as a regular input request."""

    def __init__(self, parent_request: InputRequest):
        self.parent_request = parent_request

    def execute(self) -> None:
        from engine.game_state import game_state

        menu_options = [
            Option(
                name=LocalStr("ui.menu_info_player", default="Info: player"),
                actions=[
                    LambdaAction(func=self._show_player_info, args=[game_state]),
                    MenuAction(self.parent_request),
                ],
                commands=["player"],
            ),
            Option(
                name=LocalStr("ui.menu_info_deck", default="Info: deck"),
                actions=[
                    LambdaAction(func=self._show_deck_info, args=[game_state]),
                    MenuAction(self.parent_request),
                ],
                commands=["deck"],
            ),
            Option(
                name=LocalStr("ui.menu_info_relics", default="Info: relics"),
                actions=[
                    LambdaAction(func=self._show_relics_info, args=[game_state]),
                    MenuAction(self.parent_request),
                ],
                commands=["relics"],
            ),
            Option(
                name=LocalStr("ui.menu_save", default="Save"),
                actions=[
                    LambdaAction(func=self._save_game, args=[game_state]),
                    MenuAction(self.parent_request),
                ],
                commands=["save"],
            ),
            Option(
                name=LocalStr("ui.menu_return", default="Return"),
                actions=[ResumeInputRequestAction(self.parent_request)],
                commands=["return", "back"],
            ),
            Option(
                name=LocalStr("ui.menu_exit", default="Exit"),
                actions=[LambdaAction(func=self._exit_game)],
                commands=["exit", "quit"],
            ),
        ]
        request_input(
            InputRequest(
                title=LocalStr("ui.menu_title", default="Game Menu"),
                options=menu_options,
                max_select=1,
                must_select=True,
                request_type="selection",
                allow_menu=False,
            )
        )

    def _show_player_info(self, gs):
        player = gs.player
        lines = [
            f"HP: {player.hp}/{player.max_hp}",
            f"Gold: {player.gold}",
            f"Energy: {getattr(player, 'energy', 0)}",
        ]
        self._emit_lines(lines)

    def _show_deck_info(self, gs):
        deck = gs.player.card_manager.get_pile("deck")
        lines = ["Deck:"] + [f"- {card.info()}" for card in deck]
        self._emit_lines(lines)

    def _show_relics_info(self, gs):
        lines = ["Relics:"] + [f"- {relic.info()}" for relic in gs.player.relics]
        self._emit_lines(lines)

    def _save_game(self, gs):
        import os
        import pickle
        import tempfile

        save_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "savegame.pkl"))
        temporary_path = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="wb", dir=os.path.dirname(save_path),
                prefix=".savegame-", suffix=".tmp", delete=False,
            ) as f:
                temporary_path = f.name
                pickle.dump(gs, f)
                f.flush()
                os.fsync(f.fileno())
            os.replace(temporary_path, save_path)
        finally:
            if temporary_path is not None and os.path.exists(temporary_path):
                os.unlink(temporary_path)
        self._emit_lines(["Game saved."])

    def _exit_game(self):
        from engine.game_state import game_state

        set_terminal_state(GameTerminalState.GAME_EXIT)
        return

    @staticmethod
    def _emit_lines(lines: List[str]):
        emit_lines(lines)
        flush_runtime_events()
