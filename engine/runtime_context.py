import random as rd
import sys
import os
from typing import List, Optional, cast

from engine.input_protocol import InputRequest, InputSubmission
from utils.option import Option, match_option_command, option_label, selection_error

NO_OVERRIDE = object()




def _is_stream_interactive(stream) -> bool:
    """Return True when a stream is attached to an interactive terminal."""
    if stream is None:
        return False
    try:
        if not bool(stream.isatty()):
            return False
    except (AttributeError, OSError, ValueError):
        return False
    try:
        os.get_terminal_size(stream.fileno())
    except (AttributeError, OSError, ValueError):
        try:
            stream.fileno()
        except (AttributeError, OSError, ValueError):
            return True
        return False
    return True


def is_stdin_interactive(stdin=None, stdout=None) -> bool:
    """Return True only when CLI stdin/stdout can support interactive input/output."""
    input_stream = stdin if stdin is not None else sys.stdin
    output_stream = stdout if stdout is not None else sys.stdout
    return _is_stream_interactive(input_stream) and _is_stream_interactive(output_stream)


def configure_noninteractive_cli_mode(game_state, stdin=None, stdout=None) -> bool:
    """Switch the game into a stable non-interactive CLI mode when stdin is unavailable."""
    if is_stdin_interactive(stdin, stdout):
        return False

    config = getattr(game_state, "config", None)
    if config is None:
        return False

    config.mode = "debug"
    config.auto_select = True
    debug = getattr(config, "debug", None)
    if not isinstance(debug, dict):
        debug = {}
        config.debug = debug
    debug["select_type"] = "first"
    return True

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

    def _call_game_state_override(self, hook_name, *args, **kwargs):
        """Call an overridden GameState hook when one is present."""
        if self.game_state is None:
            return NO_OVERRIDE

        bound = getattr(self.game_state, hook_name, None)
        if bound is None:
            return NO_OVERRIDE

        from engine.game_state import _GAME_STATE_RUNTIME_HOOK_WRAPPERS

        default_impl = _GAME_STATE_RUNTIME_HOOK_WRAPPERS.get(hook_name)
        target_impl = getattr(bound, "__func__", bound)
        if default_impl is not None and target_impl is default_impl:
            return NO_OVERRIDE

        return bound(*args, **kwargs)

    @staticmethod
    def _coerce_selected_indices(value: object) -> List[int]:
        if not isinstance(value, list) or any(not isinstance(index, int) or isinstance(index, bool) for index in value):
            return [-1]
        return cast(List[int], value)

    @staticmethod
    def _coerce_submission(value: object) -> InputSubmission:
        if isinstance(value, InputSubmission):
            return value
        return InputSubmission([])

    def _augment_noncombat_potion_options(self, request: InputRequest) -> InputRequest:
        """Append non-combat potion options to a selection request when applicable."""
        from actions.combat import UsePotionAction
        from actions.display import ResumeInputRequestAction
        from localization import LocalStr

        if request.request_type != "selection" or self.current_combat is not None:
            return request

        player = self.player
        if player is None:
            return request

        base_options = list(request.options or [])
        augmented_options = list(base_options)
        for potion in list(getattr(player, "potions", []) or []):
            if getattr(potion, "event_locked", False):
                continue
            if not getattr(potion, "can_be_used_actively", True):
                continue
            if not getattr(potion, "can_be_used_out_of_combat", False):
                continue
            augmented_options.append(
                Option(
                    name=LocalStr(
                        "ui.use_potion_option",
                        default=f"Use potion: {potion.local('name').resolve()}",
                    ),
                    actions=[
                        UsePotionAction(potion=potion, target=player),
                        ResumeInputRequestAction(request),
                    ],
                    commands=[f"potion{len(augmented_options)}", getattr(potion, "idstr", "")],
                )
            )

        if len(augmented_options) == len(base_options):
            return request

        return InputRequest(
            title=request.title,
            options=augmented_options,
            max_select=request.max_select,
            must_select=request.must_select,
            context=dict(request.context or {}),
            request_type=request.request_type,
            allow_menu=request.allow_menu,
        )

    def message_participants(self, enemies=None, include_hand=False, hand=None) -> List:
        """Build the standard runtime participant list for message dispatch."""
        participants = []
        player = self.player
        if player is not None:
            participants.append(player)
            participants.extend(list(getattr(player, "relics", [])))
            participants.extend(list(getattr(player, "powers", [])))
            orb_manager = getattr(player, "orb_manager", None)
            if orb_manager is not None:
                participants.extend(list(getattr(orb_manager, "orbs", [])))

        enemy_list = list(enemies or [])
        participants.extend(enemy_list)
        for enemy in enemy_list:
            participants.extend(list(getattr(enemy, "powers", [])))

        if include_hand:
            if hand is None and player is not None and getattr(player, "card_manager", None):
                hand = list(player.card_manager.get_pile("hand"))
            participants.extend(list(hand or []))

        return participants

    def message_participants_for_message(self, message) -> List:
        """Infer runtime participants from a published message."""
        participants = []
        seen = set()

        def add_participant(participant):
            if participant is None:
                return
            marker = id(participant)
            if marker in seen:
                return
            seen.add(marker)
            participants.append(participant)

        def add_creature(creature):
            add_participant(creature)
            for relic in list(getattr(creature, "relics", []) or []):
                add_participant(relic)
            for power in list(getattr(creature, "powers", []) or []):
                add_participant(power)
            orb_manager = getattr(creature, "orb_manager", None)
            if orb_manager is not None:
                for orb in list(getattr(orb_manager, "orbs", []) or []):
                    add_participant(orb)

        def add_player_cards():
            player = self.player
            card_manager = getattr(player, "card_manager", None)
            if card_manager is None:
                return
            for pile_name in ("hand", "draw_pile", "discard_pile", "exhaust_pile"):
                for pile_card in list(card_manager.get_pile(pile_name) or []):
                    add_participant(pile_card)

        if type(message).__name__ == "EnemyDefeatedMessage":
            # The original onMonsterDeath relic phase follows power onDeath,
            # including half-dead transitions, without permanent-death hooks.
            return list(getattr(self.player, "relics", []))

        if type(message).__name__ == "EnemyHpDepletedMessage":
            # Half-dead transitions notify the owner's powers before cleanup,
            # without invoking the creature's permanent-death handler.
            for power in list(getattr(message.creature, "powers", [])):
                add_participant(power)
            return participants

        if type(message).__name__ == "CreatureDiedMessage":
            add_creature(getattr(message, "creature", None))
            add_participant(getattr(message, "card", None))
            return participants

        add_creature(getattr(message, "owner", None))
        add_creature(getattr(message, "target", None))
        add_creature(getattr(message, "source", None))
        add_creature(getattr(message, "creature", None))

        for enemy in list(getattr(message, "enemies", []) or []):
            add_creature(enemy)

        for entity in list(getattr(message, "entities", []) or []):
            add_creature(entity)

        for target in list(getattr(message, "targets", []) or []):
            add_creature(target)

        if type(message).__name__ == "CardPlayedMessage" and getattr(message, "owner", None) is self.player:
            combat = self.current_combat
            for enemy in list(getattr(combat, "enemies", []) or []):
                if enemy.is_dead():
                    continue
                for power in list(getattr(enemy, "powers", []) or []):
                    if getattr(power, "observes_all_player_card_plays", False):
                        add_participant(power)

        for hand_card in list(getattr(message, "hand_cards", []) or []):
            add_participant(hand_card)

        add_participant(getattr(message, "card", None))
        add_participant(getattr(message, "power", None))
        add_participant(getattr(message, "potion", None))
        add_participant(getattr(message, "relic", None))

        if type(message).__name__ in {
            "CardPlayedMessage",
            "DamageDealtMessage",
            "FatalDamageMessage",
            "HpLostMessage",
            "DirectHpLossMessage",
            "AnyHpLostMessage",
            "PhysicalAttackTakenMessage",
            "PhysicalAttackDealtMessage",
            "ScryMessage",
            "StanceChangedMessage",
        }:
            add_player_cards()

        return participants

    def resolve_input_request(self, request: InputRequest) -> InputSubmission:
        """Resolve one declarative input request based on the configured mode."""
        request = self._augment_noncombat_potion_options(request)
        if request.request_type != "selection":
            return InputSubmission([])

        options = list(request.options or [])
        if not options:
            return InputSubmission([])

        from localization import t
        from tui.print_utils import tui_print

        config = self.config
        mode = str(getattr(config, "mode", "human"))
        human_mode = mode not in ("ai", "debug")
        attempts = 0
        while True:
            submission_options = options
            if human_mode:
                options_obj = self._call_game_state_override("_augment_human_options", request)
                submission_options = cast(List[Option], self.default_augment_human_options(request)) if options_obj is NO_OVERRIDE else cast(List[Option], options_obj)
            available_count = sum(bool(getattr(option, "enabled", True)) for option in submission_options)
            required = available_count if request.max_select == -1 else request.max_select
            if request.must_select and (available_count == 0 or required > available_count):
                raise ValueError(t("ui.selection_unavailable"))
            if not available_count:
                return InputSubmission([])
            if bool(getattr(config, "auto_select", False)) and len(submission_options) == 1 and required == 1:
                selected_indices = [0]
            else:
                hook = "_resolve_human_selection" if human_mode else "_resolve_ai_selection" if mode == "ai" else "_resolve_debug_selection"
                selected_obj = self._call_game_state_override(hook, request)
                if selected_obj is NO_OVERRIDE:
                    resolver = self.default_resolve_human_selection if human_mode else self.default_resolve_ai_selection if mode == "ai" else self.default_resolve_debug_selection
                    selected_obj = resolver(request)
                selected_indices = self._coerce_selected_indices(selected_obj)
            error = selection_error(submission_options, selected_indices, request.max_select, request.must_select)
            if error is None:
                break
            tui_print(error)
            attempts += 1
            if not human_mode and attempts >= 3:
                raise ValueError(error)

        submission_obj = self._call_game_state_override("_build_submission", submission_options, selected_indices)
        if submission_obj is NO_OVERRIDE:
            return self.default_build_submission(submission_options, selected_indices)
        return self._coerce_submission(submission_obj)

    def default_augment_human_options(self, request: InputRequest) -> List:
        """Add human-only helper options such as the in-run menu."""
        import sys
        from localization import LocalStr
        from tui import is_tui_mode

        request = self._augment_noncombat_potion_options(request)
        options = list(request.options or [])

        config = self.config
        human_config = getattr(config, "human", {}) if config is not None else {}
        show_menu = bool(getattr(human_config, "get", lambda *_args, **_kwargs: False)("show_menu_option", False))
        interactive_cli = is_stdin_interactive()
        if not request.allow_menu or not show_menu or not (interactive_cli or is_tui_mode()):
            return options

        from actions.display import MenuAction
        from localization import LocalStr

        options.append(
            Option(
                name=LocalStr("ui.open_menu", default="Open the menu"),
                actions=[MenuAction(request)],
            )
        )
        return options

    def default_resolve_human_selection(self, request: InputRequest) -> List[int]:
        """Resolve a selection request from CLI or TUI human input."""
        from localization import resolve_text, t
        from tui import get_app, is_tui_mode
        from tui.print_utils import tui_print

        options_obj = self._call_game_state_override("_augment_human_options", request)
        if options_obj is NO_OVERRIDE:
            options = cast(List[Option], self.default_augment_human_options(request))
        elif isinstance(options_obj, list):
            options = cast(List[Option], options_obj)
        else:
            options = []
        title = resolve_text(request.title)

        if is_tui_mode():
            app = get_app()
            if app:
                while True:
                    indices = app.request_selection_sync(
                        title=title, options=options, max_select=request.max_select,
                        must_select=request.must_select,
                    )
                    if selection_error(options, indices, request.max_select, request.must_select) is None:
                        return indices

        while True:
            if title:
                tui_print(title)

            for idx, option in enumerate(options, start=1):
                tui_print(f"  {idx}. {option_label(option)}")
                detail = getattr(option, "detail", None)
                if detail:
                    tui_print(f"     {resolve_text(detail)}")

            if request.must_select:
                prompt = t("ui.select_prompt", count=len(options))
            else:
                tui_print(f"  0. {t('ui.selection_skip')}")
                prompt = t("ui.select_prompt_optional", count=len(options))

            raw = input(prompt)
            command_match = match_option_command(raw, options)
            if command_match is not None:
                error = selection_error(options, command_match, request.max_select, request.must_select)
                if error is None:
                    return command_match
                tui_print(error)
                continue
            parsed_obj = self._call_game_state_override(
                "_parse_selection_input",
                raw_input=raw,
                option_count=len(options),
                max_select=sum(bool(getattr(option, "enabled", True)) for option in options) if request.max_select == -1 else request.max_select,
                must_select=request.must_select,
            )
            if parsed_obj is NO_OVERRIDE:
                parsed = self.default_parse_selection_input(
                    raw_input=raw,
                    option_count=len(options),
                    max_select=sum(bool(getattr(option, "enabled", True)) for option in options) if request.max_select == -1 else request.max_select,
                    must_select=request.must_select,
                )
            elif parsed_obj is None:
                parsed = None
            else:
                parsed = self._coerce_selected_indices(parsed_obj)
            if parsed is not None:
                error = selection_error(options, parsed, request.max_select, request.must_select)
                if error is None:
                    return parsed
                tui_print(error)

    def default_resolve_ai_selection(self, request: InputRequest) -> List[int]:
        """Resolve a selection request through the configured AI decision engine."""
        from tui import get_app, is_tui_mode

        options = list(request.options or [])
        if not options:
            return []

        if self.decision_engine is None:
            selected_indices_obj = self._call_game_state_override("_resolve_debug_selection", request)
            if selected_indices_obj is NO_OVERRIDE:
                return self.default_resolve_debug_selection(request)
            return self._coerce_selected_indices(selected_indices_obj)

        from localization import resolve_text, t

        title = resolve_text(request.title)
        title += "\n" + t("ui.selection_ai_rules")
        if not request.must_select:
            title += "\n" + t("ui.selection_ai_skip")
        option_text = []
        for option in options:
            name = option_label(option)
            detail = getattr(option, "detail", None)
            if detail:
                option_text.append(f"{name}\n{resolve_text(detail)}")
            else:
                option_text.append(name)
        context = dict(request.context or {})
        context["must_select"] = request.must_select
        context["disabled_indices"] = [i for i, option in enumerate(options) if not getattr(option, "enabled", True)]
        max_select = sum(bool(getattr(option, "enabled", True)) for option in options) if request.max_select == -1 else request.max_select

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

    def default_resolve_debug_selection(self, request: InputRequest) -> List[int]:
        """Select enabled options while preserving their original indices."""
        options = list(request.options or [])
        enabled_indices = [i for i, option in enumerate(options) if getattr(option, "enabled", True)]
        maximum = len(enabled_indices) if request.max_select == -1 else max(0, request.max_select)
        if maximum == 0 or not enabled_indices:
            return []
        sample_size = min(maximum, len(enabled_indices))
        config = self.config
        select_type = str(getattr(config, "get", lambda *_args, **_kwargs: "random")("debug.select_type", "random"))
        if select_type == "first":
            return enabled_indices[:sample_size]
        if select_type == "last":
            return enabled_indices[-sample_size:]
        heuristic = self._call_game_state_override("_resolve_debug_selection_with_heuristics", options, maximum)
        if heuristic is NO_OVERRIDE:
            heuristic = self.default_resolve_debug_selection_with_heuristics(options, maximum)
        if heuristic is not None:
            indices = self._coerce_selected_indices(heuristic)
            if selection_error(options, indices, request.max_select, request.must_select) is None:
                return indices
        return sorted(rd.sample(enabled_indices, sample_size))

    def default_resolve_debug_selection_with_heuristics(
        self,
        options: List,
        actual_max_select: int,
    ) -> Optional[List[int]]:
        """Prefer progress-making actions in combat before falling back to randomness."""
        if actual_max_select != 1 or not self.current_combat:
            return None

        scored = []
        for idx, option in enumerate(options):
            if not getattr(option, "enabled", True):
                continue
            score = self._call_game_state_override("_score_debug_option", option)
            if score is NO_OVERRIDE:
                score = self.default_score_debug_option(option)
            scored.append((score, idx))

        if not scored:
            return None

        best_score = max(score for score, _idx in scored)
        if best_score <= 0:
            return None

        best_indices = [idx for score, idx in scored if score == best_score]
        return [best_indices[0]]

    def default_score_debug_option(self, option) -> int:
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

    def default_parse_selection_input(
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

        parts = [part.strip() for part in raw_input.split(",")]
        numbers: List[int] = []
        for part in parts:
            if not part.isdigit():
                tui_print(t("ui.invalid_input", default="Invalid input."))
                return None
            numbers.append(int(part))

        if 0 in numbers:
            tui_print(t("ui.stop_option_mixed", default="0 can only be entered by itself."))
            return None

        if not numbers or len(numbers) != len(set(numbers)):
            tui_print(t("ui.selection_duplicate") if numbers else t("ui.invalid_input"))
            return None
        indices = [number - 1 for number in numbers]

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

    def default_build_submission(self, options: List, selected_indices: List[int]) -> InputSubmission:
        """Turn selected option indices into an actionable submission."""
        from actions.display import build_selected_options, show_selected_options

        selected_options = build_selected_options(options, selected_indices)
        if not selected_options:
            if self.game_state is not None:
                self.game_state.last_select_idx = -1
            return InputSubmission([])
        if self.game_state is not None:
            self.game_state.last_select_idx = next(iter(selected_options))
        show_selected_options(selected_options)
        actions = []
        for option in selected_options.values():
            actions.extend(option.actions)
        return InputSubmission(actions)
