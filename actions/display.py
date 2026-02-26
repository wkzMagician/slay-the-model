# -*- coding: utf-8 -*-
"""
Display-related actions - with TUI integration
"""
from typing import Dict, List, Optional
import pickle
import os
import random
import sys
from actions.base import Action
from utils.result_types import BaseResult, NoneResult, MultipleActionsResult, SingleActionResult, GameStateResult
from localization import BaseLocalStr, LocalStr, t
from utils.option import Option
from utils.registry import register


def _safe_print(text: str):
    """安全的打印函数，处理 Windows 编码问题
    
    在 Windows 平台如果遇到 UnicodeEncodeError，会自动过滤掉无法编码的字符。
    其他平台直接正常打印。
    """
    try:
        print(text)
    except UnicodeEncodeError:
        # 如果失败，过滤掉无法编码的字符
        safe_text = text.encode('utf-8', errors='replace').decode('utf-8')
        print(safe_text)

def get_game_state():
    from engine.game_state import game_state
    return game_state

def _is_tui_mode():
    """Check if TUI mode is active."""
    try:
        from tui import is_tui_mode, get_app
        return is_tui_mode() and get_app() is not None
    except ImportError:
        return False

def _get_tui_app():
    """Get TUI app instance if available."""
    try:
        from tui import get_app
        return get_app()
    except ImportError:
        return None

@register("action")
class DisplayTextAction(Action):
    """Display text to user - routes to TUI output panel when available

    Required:
        text_key (str): key for localized text

    Optional:
        None
    """
    def __init__(self, text_key: str = "", **fmt):
        self.text_key = text_key
        self.fmt = fmt

    def execute(self) -> 'BaseResult':
        # Extract default from fmt if present, otherwise use text_key
        fallback = self.fmt.get('default', self.text_key)
        text = t(self.text_key, default=fallback, **{k: v for k, v in self.fmt.items() if k != 'default'})
        
        # Route to TUI if available
        app = _get_tui_app()
        if app:
            app.add_output(text)
        else:
            print(text)
        return NoneResult()

@register("action")
class SelectAction(Action):
    """向用户展示选项并返回所选的动作列表。
    
    参数：
        title (BaseLocalStr): 选择标题的本地化键
        options (List[Option]): 可供选择的选项列表
        max_select (int): 最大选择数量（-1表示全选，1表示单选，>1表示多选）
        must_select (bool): 是否必须选满（True必须选满，False可以提前停止）

    自动化行为：
        - 无选项时自动前进（返回空列表）
        - max_select=-1 且 must_select=True 时自动选择所有选项（不包含菜单选项）
        - must_select=True 时：
          * 非人类模式或 auto_select=True 时自动选择
          * 仅有一个选项时自动选择该选项
          * max_select <= len(options) 时自动选择前max_select个选项（不包含菜单选项）
        - must_select=False 时：
          * 禁止所有自动选择，必须交互
          * 可提前停止选择
    """

    def __init__(self, title : BaseLocalStr = None, options : List[Option] = None, max_select: int = 1, must_select: bool = True, context: Dict = None):
        # Support both 'title' and 'prompt' for backward compatibility
        self.title = title
        self.options = options if options is not None else []
        self.max_select = max_select
        self.must_select = must_select
        self.context = context or {}
        self.has_menu = False
        self.options = options if options is not None else []
        self.max_select = max_select
        self.must_select = must_select
        self.has_menu = False

    def execute(self) -> 'BaseResult':
        """执行选择流程，返回需要执行的动作列表。"""
        
        # [0] 无选项时自动前进
        if len(self.options) == 0:
            return NoneResult()
        
        mode = get_game_state().config.get("mode", "debug")
        
        if mode == 'human':
            return self.execute_human()
        elif mode == 'ai':
            return self.execute_ai()
        elif mode == 'debug':
            return self.execute_debug()
        else:
            raise ValueError("Invalid Mode!")
        
    def show_info(self):
        # 展示标题与选项（翻译 name）
        # If title is a plain string that looks like a localization key, localize it
        app = _get_tui_app()
        
        if isinstance(self.title, str):
            title_str = f"=== {t(self.title)} ==="
        else:
            title_str = f"=== {self.title} ==="
        
        options_lines = []
        for i, option in enumerate(self.options):
            options_lines.append(f"{i+1}. {option.name}")
        
        if app:
            # Route to TUI selection panel
            app.show_selection(title_str, self.options)
        else:
            print(f"\n{title_str}")
            for line in options_lines:
                print(line)
            
    def _build_selected_options(
        self,
        options: List[Option],
        selected_indices: List[int],
    ) -> Dict[int, Option]:
        """Build selected options map with original index as key."""
        return {
            idx: options[idx]
            for idx in selected_indices
            if 0 <= idx < len(options)
        }

    def show_choose(self, selected_options: Dict[int, Option]):
        """Print the selected options
        
        Args:
            selected_options: Mapping of original index -> selected option
        """
        if not selected_options:
            return
        
        app = _get_tui_app()
        # Print selection header
        header = f"\n{t('ui.selected', default='Selected:')}"
        lines = [header]
        for idx, option in selected_options.items():
            lines.append(f"  {idx+1}. {option.name}")
        
        if app:
            for line in lines:
                app.add_output(line)
        else:
            for line in lines:
                print(line)

    def _execute_human_tui(
        self,
        options: List[Option],
        actual_max_select: int,
    ) -> 'BaseResult':
        """Execute human selection using the TUI async bridge."""
        app = _get_tui_app()
        if app is None:
            return NoneResult()

        if isinstance(self.title, str):
            title_str = t(self.title)
        else:
            title_str = str(self.title)

        selected_indices = app.request_selection_sync(
            title_str,
            options,
            self.max_select,
            self.must_select,
        )

        if not selected_indices:
            return NoneResult()

        valid_indices = list(dict.fromkeys(selected_indices))

        if not self.must_select and 0 in valid_indices:
            if len(valid_indices) > 1:
                app.add_output(
                    t(
                        "ui.stop_option_mixed",
                        default=(
                            "WARNING: Cannot select stop option with "
                            "other options. Please select again."
                        ),
                    )
                )
                return self._execute_human_tui(options, actual_max_select)
            return NoneResult()

        if self.has_menu:
            menu_idx = len(options) - 1
            if menu_idx in valid_indices:
                if len(valid_indices) > 1:
                    app.add_output(
                        t(
                            "ui.menu_option_mixed",
                            default=(
                                "WARNING: Cannot select menu option with "
                                "other options. Please select again."
                            ),
                        )
                    )
                    return self._execute_human_tui(options, actual_max_select)
                return MultipleActionsResult(options[menu_idx].actions)

        if len(valid_indices) > actual_max_select:
            overflow_handling = get_game_state().config.get(
                "select_overflow",
                "truncate",
            )

            if overflow_handling == "truncate":
                app.add_output(
                    t(
                        "ui.too_many_options_truncated",
                        default=(
                            f"Too many options selected (max "
                            f"{actual_max_select}), truncating to first "
                            f"{actual_max_select}"
                        ),
                    )
                )
                valid_indices = valid_indices[:actual_max_select]
            else:
                app.add_output(
                    t(
                        "ui.too_many_options",
                        default=(
                            f"Too many options selected (max "
                            f"{self.max_select})"
                        ),
                    )
                )
                return self._execute_human_tui(options, actual_max_select)

        selected_options = self._build_selected_options(options, valid_indices)
        self.show_choose(selected_options)

        selected_actions = []
        for idx in valid_indices:
            selected_actions.extend(options[idx].actions)
        return MultipleActionsResult(selected_actions)
        
        
    def execute_human(self) -> 'BaseResult':
        human_module = get_game_state().config.get("human")
        
        options = self.options.copy()
            
        # [option] 如果不是必须选满，允许用户提前停止选择
        if not self.must_select:
            # 插入到第一个位置，方便用户输入0停止选择
            options.insert(0, Option(name=LocalStr("ui.stop_selection", default="Stop selection"), actions=[]))
            
        options_no_menu = options
            
        # [option] 是否有菜单选项
        if human_module.get("show_menu_option", True):
            menu_option = Option(
                name=LocalStr("ui.open_menu"),
                actions=[MenuAction(self)]
            )
            options.append(menu_option)
            options_no_menu = options[:-1]
            self.has_menu = True
            
        # print
        self.show_info()
        
        # [auto] 全选
        if self.max_select == -1 and self.must_select:
            all_actions = []
            
            # Print selected options
            selected_options = self._build_selected_options(
                options_no_menu,
                list(range(len(options_no_menu))),
            )
            self.show_choose(selected_options)
            
            for option in options_no_menu: # 除了菜单
                all_actions.extend(option.actions)
            return MultipleActionsResult(all_actions)
        
         # [auto] 必须选择的数量>=选择数量时，如果自动选择为True，那么就全选
        if self.must_select and human_module.get("auto_select", False) \
                and self.max_select >= len(options_no_menu): # 除了菜单
            all_actions = []
            selected_indices = list(range(self.max_select))
            selected_options = self._build_selected_options(
                options_no_menu,
                selected_indices,
            )
            
            # Print selected options
            self.show_choose(selected_options)
            
            for option in selected_options.values():
                all_actions.extend(option.actions)
            return MultipleActionsResult(all_actions)
        
        actual_max_select = self.max_select if self.max_select != -1 else len(options)

        if _is_tui_mode():
            return self._execute_human_tui(options, actual_max_select)
        
        while True:
            try:
                # 构造提示信息
                if self.must_select:
                    prompt_text = t(
                        "ui.multi_select_prompt",
                        default=f"Choose {actual_max_select} options (comma-separated, e.g., 1,3,5): ",
                        max_count=actual_max_select,
                    )
                else:
                    prompt_text = t(
                        "ui.multi_select_optional_prompt",
                        default=f"Choose up to {actual_max_select} options (comma-separated, e.g., 1,3,5), or enter 0 to stop: ",
                        max_count=actual_max_select,
                    )
                
                input_str = input(prompt_text).strip()
                
                # 解析输入
                selected_indices = []
                for part in input_str.split(','):
                    part = part.strip()
                    if part:
                        selected_indices.append(int(part) - 1)
                
                # 验证选择
                valid_indices = []
                for idx in selected_indices:
                    if 0 <= idx < len(options):
                        valid_indices.append(idx)
                    else:
                        print(t("ui.invalid_option", default=f"Invalid option: {idx+1}"))
                        break
                # 去除重复选择
                valid_indices = list(dict.fromkeys(valid_indices))
                
                if len(valid_indices) != len(selected_indices):
                    continue
                
                # 只允许stop_option被单选
                if not self.must_select and valid_indices.count(0) == 1:
                    if len(valid_indices) > 1:
                        print(t("ui.stop_option_mixed", default="WARNING: Cannot select stop option with other options. Please select again."))
                        continue
                    else: # 返回空动作列表，表示用户选择停止选择
                        return NoneResult()
                
                # 如果菜单选项和其他选项同时被选择，警告并重新选择
                if self.has_menu:
                    menu_idx = len(options) - 1
                    if valid_indices.count(menu_idx) == 1:
                        if len(valid_indices) > 1:
                            print(t("ui.menu_option_mixed", default="WARNING: Cannot select menu option with other options. Please select again."))
                            continue
                        else: # 选择了菜单选项，直接返回菜单动作
                            return MultipleActionsResult(options[menu_idx].actions)
                
                if len(valid_indices) > actual_max_select:
                    # 从config读取处理方式：truncate或reselect
                    overflow_handling = get_game_state().config.get("select_overflow", "truncate")
                    
                    if overflow_handling == "truncate":
                        print(t("ui.too_many_options_truncated", default=f"Too many options selected (max {actual_max_select}), truncating to first {actual_max_select}"))
                        # 截断前max_select个选项
                        actual_indices = [idx for idx in valid_indices if idx < len(options)]
                        actual_indices = actual_indices[:actual_max_select]
                        
                        # Print selected options
                        selected_options = self._build_selected_options(
                            options,
                            actual_indices,
                        )
                        self.show_choose(selected_options)
                        
                        # 收集动作
                        selected_actions = []
                        for idx in actual_indices:
                            selected_actions.extend(options[idx].actions)
                        return MultipleActionsResult(selected_actions)
                    else:  # reselect
                        print(t("ui.too_many_options", default=f"Too many options selected (max {self.max_select})"))
                        continue
                
                # 如果是必须选满且未选满，重新选择
                if self.must_select and len(valid_indices) < actual_max_select:
                    print(f"Selected {len(valid_indices)} options, but {actual_max_select} required.")
                    continue
                
                # Print selected options
                selected_options = self._build_selected_options(
                    options,
                    valid_indices,
                )
                self.show_choose(selected_options)
                
                # 收集所有选择的动作
                selected_actions = []
                for idx in valid_indices:
                    selected_actions.extend(options[idx].actions)
                return MultipleActionsResult(selected_actions)
                    
            except (ValueError, EOFError):
                print(t("ui.invalid_input", default="Invalid input format. Use comma-separated numbers."))
        
    def execute_ai(self) -> 'BaseResult':
        """AI mode selection using LLM Decision Engine."""
        from engine.game_state import game_state
        
        from ai.context_builder import AIContextBuilder
        engine = game_state.decision_engine
        if engine is None:
            # No decision engine - cannot make decision
            return NoneResult()
        
        options = self.options.copy()
        
        # Add stop option if not must_select
        if not self.must_select:
            options.insert(0, Option(name=LocalStr("ui.stop_selection", default="Stop selection"), actions=[]))
        
        self.show_info()
        
        # Get TUI app for showing thinking message
        app = _get_tui_app()
        
        # Build option descriptions
        option_texts = []
        for opt in options:
            desc = getattr(opt, 'description', None) or getattr(opt, 'name', None) or str(opt)
            option_texts.append(str(desc))
        
        # Call AI decision engine
        actual_max_select = self.max_select if self.max_select != -1 else len(options)
        
        # Check if engine supports streaming
        thinking_result = None
        is_stream_mode = hasattr(engine, 'client') and getattr(engine.client, 'stream', False)
        
        if app:
            # TUI mode: show "AI thinking" message in selection panel
            selection_panel = app.get_selection_panel()
            if selection_panel:
                thinking_msg = t("ai.ai_thinking", default="AI 正在思考中...")
                selection_panel.show_thinking(thinking_msg)
            
            # Use non-streaming method for TUI (TUI has its own display mechanism)
            if hasattr(engine, 'make_decision_with_thinking'):
                selected_indices, thinking_result = engine.make_decision_with_thinking(
                    title=str(self.title),
                    options=option_texts,
                    context={"game_state": AIContextBuilder.build_context(game_state)},
                    max_select=actual_max_select,
                )
            else:
                selected_indices = engine.make_decision(
                    title=str(self.title),
                    options=option_texts,
                    context={"game_state": AIContextBuilder.build_context(game_state)},
                    max_select=actual_max_select,
                )
        else:
            # no-TUI mode: print "AI thinking" before sending prompt
            thinking_msg = t("ai.ai_thinking", default="AI 正在思考中...")
            _safe_print(f"\n{thinking_msg}")
            
            # Streaming callback for real-time output
            def streaming_callback(chunk_type: str, content: str):
                """Callback for streaming output in no-TUI mode."""
                if chunk_type == "thinking":
                    # Real-time thinking output (no newline prefix, just print as-is)
                    _safe_print(content)
                elif chunk_type == "answer":
                    # Real-time answer output
                    _safe_print(content)
            
            # Use streaming method if available and stream mode is enabled
            if is_stream_mode and hasattr(engine, 'make_decision_with_streaming'):
                selected_indices, thinking_result = engine.make_decision_with_streaming(
                    title=str(self.title),
                    options=option_texts,
                    context={"game_state": AIContextBuilder.build_context(game_state)},
                    max_select=actual_max_select,
                    streaming_callback=streaming_callback,
                )
                # Print newline after streaming completes
                _safe_print("")
            elif hasattr(engine, 'make_decision_with_thinking'):
                selected_indices, thinking_result = engine.make_decision_with_thinking(
                    title=str(self.title),
                    options=option_texts,
                    context={"game_state": AIContextBuilder.build_context(game_state)},
                    max_select=actual_max_select,
                )
            else:
                selected_indices = engine.make_decision(
                    title=str(self.title),
                    options=option_texts,
                    context={"game_state": AIContextBuilder.build_context(game_state)},
                    max_select=actual_max_select,
                )
        
        # Show thinking and answer in output panel (TUI) or stdout (no-TUI)
        # For streaming mode, content is already printed in real-time, so skip re-printing
        answer_text = getattr(engine, '_last_answer', None)
        
        if app:
            # TUI mode: show in output panel
            output_panel = app.get_output_panel()
            if output_panel:
                finished_msg = t("ai.ai_thinking_finished", default="AI 思考完成")
                output_panel.add_combat_message(f"\n{finished_msg}")
                
                # Show thinking content (full content)
                if thinking_result and len(thinking_result) > 0:
                    thinking_header = t("ai.thinking_header", default="=== AI 思考过程 ===")
                    output_panel.add_state_message(thinking_header)
                    # Split by newlines and add each line
                    for line in thinking_result.split('\n'):
                        if line.strip():
                            output_panel.add_state_message(f"  {line}")
                
                # Show answer content
                if answer_text and len(answer_text) > 0:
                    answer_header = t("ai.answer_header", default="=== AI 回答 ===")
                    output_panel.add_combat_message(answer_header)
                    for line in answer_text.split('\n'):
                        if line.strip():
                            output_panel.add_combat_message(f"  {line}")
        else:
            # no-TUI mode: for non-streaming, print thinking and answer
            # For streaming mode, content is already printed in real-time
            if not is_stream_mode:
                finished_msg = t("ai.ai_thinking_finished", default="AI 思考完成")
                _safe_print(f"\n{finished_msg}")
                
                # Show thinking content (full content)
                if thinking_result and len(thinking_result) > 0:
                    thinking_header = t("ai.thinking_header", default="=== AI 思考过程 ===")
                    _safe_print(thinking_header)
                    for line in thinking_result.split('\n'):
                        if line.strip():
                            _safe_print(f"  {line}")
                
                # Show answer content
                if answer_text and len(answer_text) > 0:
                    answer_header = t("ai.answer_header", default="=== AI 回答 ===")
                    _safe_print(answer_header)
                    for line in answer_text.split('\n'):
                        if line.strip():
                            _safe_print(f"  {line}")
        
        if not selected_indices:
            # AI returned no valid selection
            return NoneResult()
        
        # Handle stop option (index 0 when must_select=False)
        if not self.must_select and 0 in selected_indices:
            return NoneResult()
        
        # Print selected options
        selected_options = self._build_selected_options(options, selected_indices)
        self.show_choose(selected_options)
        
        # Collect actions
        selected_actions = []
        for idx in selected_indices:
            if 0 <= idx < len(options):
                selected_actions.extend(options[idx].actions)
        
        return MultipleActionsResult(selected_actions)











    

    def execute_debug(self) -> 'BaseResult':
        debug_module = get_game_state().config.get("debug")
        
        options = self.options.copy()
        
        self.show_info()
        
        select_idxs = []
        # 确定要选择的数量
        if self.max_select == -1:
            # max_select=-1时选择所有选项（不包含菜单选项）
            num_to_select = len(options)
            select_idxs = list(range(num_to_select))
        else:
            num_to_select = min(self.max_select, len(options))
            
            select_type = debug_module.get("select_type", "random")
            if select_type == "random":
                import random
                select_idxs = random.sample(range(len(options)), num_to_select)
            elif select_type == "first":
                select_idxs = list(range(num_to_select))
            elif select_type == "last":
                select_idxs = list(range(len(options) - num_to_select, len(options)))
            else:
                raise ValueError(f"Invalid debug select_type: {select_type}")
            
        # Print selected options
        selected_options = self._build_selected_options(options, select_idxs)
        self.show_choose(selected_options)
        
        # 收集前num_to_select个选项的动作
        all_actions = []
        for i in select_idxs:
            all_actions.extend(options[i].actions)
        return MultipleActionsResult(all_actions)
    

@register("action")
class MenuAction(Action):
    """游戏菜单系统，提供交互式命令接口。
    
    支持的命令：
        - info player: 显示玩家信息
        - info deck: 显示卡组信息
        - info relics: 显示遗物信息
        - save: 保存当前游戏状态
        - exit: 退出游戏
        - return: 返回游戏
    """

    def __init__(self, parent_select_action: 'SelectAction'):
        self.parent_select_action = parent_select_action

    def execute(self) -> 'BaseResult':
        """执行菜单交互循环。"""
        gs = get_game_state()

        if _is_tui_mode():
            app = _get_tui_app()
            if app:
                app.add_output(
                    t(
                        "ui.menu_unavailable_tui",
                        default="Menu commands are not available in TUI mode yet.",
                    )
                )
            return SingleActionResult(self.parent_select_action)

        print("\n" + "=" * 50)
        print("游戏菜单 (输入 'help' 查看帮助)")
        print("=" * 50)

        while True:
            try:
                cmd = input("\n> ").strip().lower()
                
                if not cmd:
                    continue

                if cmd == "help":
                    self._show_help()
                elif cmd == "info player":
                    self._show_player_info(gs)
                elif cmd == "info deck":
                    self._show_deck_info(gs)
                elif cmd == "info relics":
                    self._show_relics_info(gs)
                elif cmd == "save":
                    self._save_game(gs)
                elif cmd == "exit":
                    return GameStateResult("GAME_EXIT")
                elif cmd == "return":
                    return SingleActionResult(self.parent_select_action)
                else:
                    print(f"未知命令: {cmd} (输入 'help' 查看帮助)")

            except (ValueError, EOFError, KeyboardInterrupt):
                print("\n输入错误，请重试")
            except Exception as e:
                print(f"错误: {e}")

    def _show_help(self):
        """显示帮助信息。"""
        print("\n可用命令:")
        print("  help           - 显示此帮助信息")
        print("  info player    - 显示玩家信息")
        print("  info deck      - 显示卡组信息")
        print("  info relics    - 显示遗物信息")
        print("  save           - 保存当前游戏状态")
        print("  exit           - 退出游戏")
        print("  return         - 返回游戏")

    def _show_player_info(self, gs):
        """显示玩家信息。"""
        player = gs.player
        print(f"\n--- 玩家信息 ---")
        print(f"生命值: {player.hp}/{player.max_hp}")
        print(f"能量: {player.energy}/{player.max_energy}")
        print(f"金币: {player.gold}")
        print(f"楼层: {gs.current_floor}")
        print(f"卡组数量: {len(player.deck)}")
        print(f"遗物数量: {len(player.relics)}")

    def _show_deck_info(self, gs):
        """显示卡组信息。"""
        print(f"\n--- 卡组信息 ({len(gs.player.deck)} 张) ---")
        for i, card in enumerate(gs.player.deck, 1):
            print(f"{i}. {card.name} (能量: {card.cost}, 类型: {card.card_type})")

    def _show_relics_info(self, gs):
        """显示遗物信息。"""
        print(f"\n--- 遗物信息 ({len(gs.player.relics)} 个) ---")
        for i, relic in enumerate(gs.player.relics, 1):
            print(f"{i}. {relic.local('name')}")

    def _save_game(self, gs):
        """保存当前游戏状态。"""
        save_dir = "saves"
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        timestamp = __import__('time').strftime("%Y%m%d_%H%M%S")
        save_file = os.path.join(save_dir, f"save_{timestamp}.dat")

        try:
            with open(save_file, 'wb') as f:
                pickle.dump(gs, f)
            print(f"\n游戏已保存到: {save_file}")
        except Exception as e:
            print(f"\n保存失败: {e}")
