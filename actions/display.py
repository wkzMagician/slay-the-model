# -*- coding: utf-8 -*-
"""
Display-related actions
"""
from typing import List, Optional
import pickle
import os
from actions.base import Action
from utils.result_types import BaseResult, NoneResult, MultipleActionsResult, SingleActionResult, GameStateResult
from localization import BaseLocalStr, LocalStr, t
from utils.option import Option
from utils.registry import register

def get_game_state():
    from engine.game_state import game_state
    return game_state

@register("action")
class DisplayTextAction(Action):
    """Display text to user

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

    def __init__(self, title : BaseLocalStr, options : List[Option], max_select: int = 1, must_select: bool = True):
        self.title = title
        self.options = options
        self.max_select = max_select
        self.must_select = must_select

    def execute(self) -> 'BaseResult':
        """执行选择流程，返回需要执行的动作列表。"""
        
        # [0] 无选项时报错
        assert len(self.options) > 0, "SelectAction requires at least one option"
        
        # [1] 自动选择情况 
        # [1-1] must_select=True && max_select=-1 （全选，自动）
        if self.max_select == -1 and self.must_select:
            # 收集所有选项的动作
            all_actions = []
            for option in self.options:
                all_actions.extend(option.actions)
            return MultipleActionsResult(all_actions)
        
        # [1-2] must_select=True && max_select<=len(options) （自动选择所有选项）
        if self.must_select:
            auto_select = bool(get_game_state().config.get("auto_select", False))
            is_human = get_game_state().config.get("mode") == "human"
            
            # 非人类模式或auto_select=True时自动选择
            if not is_human or auto_select:
                if self.max_select > 0 and self.max_select >= len(self.options):
                    all_actions = []
                    for option in self.options[:self.max_select]:
                        all_actions.extend(option.actions)
                    return MultipleActionsResult(all_actions)
        
        # [1-3] debug模式开启时自动选择前max_select项
        debug = get_game_state().config.get("debug", {})
        if bool(debug.get("enable", False)):
            select_idxs = []
            # 确定要选择的数量
            if self.max_select == -1:
                # max_select=-1时选择所有选项（不包含菜单选项）
                num_to_select = len(self.options)
                select_idxs = list(range(num_to_select))
            else:
                num_to_select = min(self.max_select, len(self.options))
                
                select_type = debug.get("select_type", "random")
                if select_type == "random":
                    import random
                    select_idxs = random.sample(range(len(self.options)), num_to_select)
                elif select_type == "first":
                    select_idxs = list(range(num_to_select))
                elif select_type == "last":
                    select_idxs = list(range(len(self.options) - num_to_select, len(self.options)))
                else:
                    raise ValueError(f"Invalid debug select_type: {select_type}")
            
            # 收集前num_to_select个选项的动作
            all_actions = []
            for i in select_idxs:
                all_actions.extend(self.options[i].actions)
            return MultipleActionsResult(all_actions)
        
        # [2] 交互选择
        effective_options = self.options.copy()

        # - 若为人类玩家，追加"打开菜单"选项（仅在must_select=True时）
        effective_options = self.options.copy()
        if get_game_state().config.get("mode") == "human" \
                and get_game_state().config.get("show_menu_option", True) \
                and self.must_select:
            menu_option = Option(
                name=LocalStr("ui.open_menu"),
                actions=[MenuAction(self)]
            )
            effective_options.append(menu_option)

        # 7) 根据max_select决定选择模式
        selection_mode = get_game_state().config.get("selection_mode", "single")
        
        if self.max_select == 1 or selection_mode == "single":
            # 单选模式
            return self._single_select(effective_options)
        elif selection_mode == "multi":
            # 多选模式：一次性选择多个
            return self._multi_select(effective_options)
        else:
            # 默认使用单选模式
            return self._single_select(effective_options)
    
    def _single_select(self, effective_options: List[Option]) -> 'BaseResult':
        """单选模式：一次选择一项，循环直到达到max_select数量。"""
        selected_indices = []
        selected_actions = []
        
        # 如果不是必须选满，允许用户提前停止选择
        if not self.must_select:
            # 插入到第一个位置，方便用户输入0停止选择
            effective_options.insert(0, Option(name=LocalStr("ui.stop_selection", default="Stop selection"), actions=[]))
            
        actual_max_select = self.max_select if self.max_select != -1 else len(effective_options)
        
        # 如果是单选模式，循环选择直到达到max_select或用户选择停止
        while len(selected_indices) < actual_max_select:
            try:
                # 构造提示信息
                if self.must_select:
                    prompt_text = t(
                        "ui.select_prompt",
                        default=f"Choose (1-{len(effective_options)}): ",
                        count=len(effective_options),
                    )
                else:
                    prompt_text = t(
                        "ui.select_optional_prompt",
                        default=f"Choose (1-{len(effective_options)}), or 0 to stop: ",
                        count=len(effective_options),
                    )
                
                # 展示标题与选项（翻译 name）
                print(f"\n=== {self.title} ===")
                for i, option in enumerate(effective_options):
                    print(f"{i+1}. {option.name}")
                
                option = int(input(prompt_text)) - 1
                
                # 处理"停止选择"选项（仅当must_select=False时）
                if not self.must_select and option == 0:
                    if selected_indices:
                        # 收集所有选择的动作
                        for idx in selected_indices:
                            selected_actions.extend(effective_options[idx].actions)
                        return MultipleActionsResult(selected_actions)
                    else:
                        print(t("ui.no_option_selected", default="No option selected"))
                        continue
                    
                # 如果选中了菜单选项，直接返回菜单动作， 不返回其它已选动作
                # ! 当从菜单返回时，之前的选择会全部被清除，用户需要重新选择
                menu_idx = len(effective_options) - 1 
                if option == menu_idx:
                    return MultipleActionsResult(effective_options[option].actions)
                
                # 验证选项
                if 0 <= option < len(effective_options) - 1:
                    selected_indices.append(option)
                    # 在effective_options中，删除已选择的选项，继续选择
                    effective_options.pop(option)
                else:
                    print(t("ui.invalid_option", default="Invalid option!"))
                    
            except (ValueError, EOFError):
                print(t("ui.invalid_number", default="Please enter a valid number"))
        
        for idx in selected_indices:
            selected_actions.extend(effective_options[idx].actions)
        return MultipleActionsResult(selected_actions)
    
    def _multi_select(self, effective_options: List[Option]) -> 'BaseResult':
        """多选模式：一次性选择多个选项（用逗号分隔）。"""
        menu_idx = len(effective_options) - 1
        is_human = get_game_state().config.get("mode") == "human"
        show_menu_option = bool(get_game_state().config.get("show_menu_option", True))
        
        # 如果不是必须选满，允许用户提前停止选择
        if not self.must_select:
            # 插入到第一个位置，方便用户输入0停止选择
            effective_options.insert(0, Option(name=LocalStr("ui.stop_selection", default="Stop selection"), actions=[]))
            
        actual_max_select = self.max_select if self.max_select != -1 else len(effective_options)
        
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
                    if 0 <= idx < len(effective_options):
                        valid_indices.append(idx)
                    else:
                        print(t("ui.invalid_option", default=f"Invalid option: {idx+1}"))
                        break
                # 去除重复选择
                valid_indices = list(set(valid_indices))
                
                if len(valid_indices) != len(selected_indices):
                    continue
                
                # 只允许选择一次提前停止选项（仅当must_select=False时）
                if not self.must_select:
                    stop_option_count = valid_indices.count(0)
                    if stop_option_count > 1:
                        print(t("ui.invalid_stop_option", default="Stop selection option can only be selected once."))
                        continue
                    elif stop_option_count == 1:
                        # 返回空动作列表，表示用户选择停止选择
                        return NoneResult()
                
                # 在人类模式下检查菜单选项
                if is_human and show_menu_option:
                    # 如果菜单选项和其他选项同时被选择，警告并重新选择
                    if menu_idx in valid_indices:
                        if len(valid_indices) > 1:
                            print(t("ui.menu_option_mixed", default="WARNING: Cannot select menu option with other options. Please select again."))
                            continue
                        else: # 选择了菜单选项，直接返回菜单动作
                            return MultipleActionsResult(effective_options[menu_idx].actions)
                
                if len(valid_indices) > actual_max_select:
                    # 从config读取处理方式：truncate或reselect
                    overflow_handling = get_game_state().config.get("overflow_handling", "truncate")
                    
                    if overflow_handling == "truncate":
                        print(t("ui.too_many_options_truncated", default=f"Too many options selected (max {actual_max_select}), truncating to first {actual_max_select}"))
                        # 截断前max_select个选项
                        actual_indices = [idx for idx in valid_indices if idx < len(effective_options)]
                        actual_indices = actual_indices[:actual_max_select]
                        
                        # 收集动作
                        selected_actions = []
                        for idx in actual_indices:
                            selected_actions.extend(effective_options[idx].actions)
                        return MultipleActionsResult(selected_actions)
                    else:  # reselect
                        print(t("ui.too_many_options", default=f"Too many options selected (max {self.max_select})"))
                        continue
                
                # 如果是必须选满且未选满，继续选择
                if self.must_select and len(valid_indices) < actual_max_select:
                    print(f"Selected {len(valid_indices)} options, but {actual_max_select} required.")
                    continue
                
                # 收集所有选择的动作
                selected_actions = []
                for idx in valid_indices:
                    selected_actions.extend(effective_options[idx].actions)
                
                return MultipleActionsResult(selected_actions)
                    
            except (ValueError, EOFError):
                print(t("ui.invalid_input", default="Invalid input format. Use comma-separated numbers."))


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
            print(f"{i}. {relic.name}")

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
