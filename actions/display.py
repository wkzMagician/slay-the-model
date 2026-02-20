# -*- coding: utf-8 -*-
"""
Display-related actions
"""
from typing import List, Optional
import pickle
import os
import random
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

    def __init__(self, title : BaseLocalStr = None, options : List[Option] = None, max_select: int = 1, must_select: bool = True, prompt: BaseLocalStr = None):
        # Support both 'title' and 'prompt' for backward compatibility
        self.title = title if title is not None else prompt
        self.options = options if options is not None else []
        self.max_select = max_select
        self.must_select = must_select
        self.has_menu = False

    def execute(self) -> 'BaseResult':
        """执行选择流程，返回需要执行的动作列表。"""
        
        # [0] 无选项时报错
        assert len(self.options) > 0, "SelectAction requires at least one option"
        
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
        print(f"\n=== {self.title} ===")
        for i, option in enumerate(self.options):
            print(f"{i+1}. {option.name}")
            
    def show_choose(self, options_chosen):
        """Print the selected options
        
        Args:
            options_chosen: List of Option objects that were selected
        """
        if not options_chosen:
            return
        
        # Print selection header
        print(f"\n{t('ui.selected', default='Selected:')}")
        for i, option in enumerate(options_chosen, 1):
            print(f"  {i}. {option.name}")
        
        
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
            self.show_choose(options_no_menu)
            
            for option in options_no_menu: # 除了菜单
                all_actions.extend(option.actions)
            return MultipleActionsResult(all_actions)
        
         # [auto] 必须选择的数量>=选择数量时，如果自动选择为True，那么就全选
        if self.must_select and human_module.get("auto_select", False) \
                and self.max_select >= len(options_no_menu): # 除了菜单
            all_actions = []
            selected_options = options_no_menu[:self.max_select]
            
            # Print selected options
            self.show_choose(selected_options)
            
            for option in selected_options:
                all_actions.extend(option.actions)
            return MultipleActionsResult(all_actions)
        
        actual_max_select = self.max_select if self.max_select != -1 else len(options)
        
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
                valid_indices = list(set(valid_indices))
                
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
                        selected_options = [options[idx] for idx in actual_indices]
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
                selected_options = [options[idx] for idx in valid_indices]
                self.show_choose(selected_options)
                
                # 收集所有选择的动作
                selected_actions = []
                for idx in valid_indices:
                    selected_actions.extend(options[idx].actions)
                return MultipleActionsResult(selected_actions)
                    
            except (ValueError, EOFError):
                print(t("ui.invalid_input", default="Invalid input format. Use comma-separated numbers."))
        
    def execute_ai(self) -> 'BaseResult':
        ai_module = get_game_state().config.get("ai")
        options = self.options.copy()
        # 如果不是必须选满，允许用户提前停止选择
        if not self.must_select:
            # 插入到第一个位置，方便用户输入0停止选择
            options.insert(0, Option(name=LocalStr("ui.stop_selection", default="Stop selection"), actions=[]))
            
        self.show_info()
        # todo: 和human模式基本一致，但把input改为调用接口，获得返回数据
        return NoneResult()
        
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
        selected_options = [options[i] for i in select_idxs]
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
