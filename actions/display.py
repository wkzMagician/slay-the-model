# -*- coding: utf-8 -*-
"""
Display-related actions
"""
from typing import List, Optional
from actions.base import Action
from utils.result_types import BaseResult, NoneResult, MultipleActionsResult
from localization import BaseLocalStr, t
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

    自动化行为：
        - 仅有一个选项时可自动选择（AI 或配置允许时）
        - 无选项时自动前进（返回空列表）
        - AI 调试模式可自动选择第一项
    """

    def __init__(self, title : BaseLocalStr, options : List[Option]):
        self.title = title
        self.options = options

    def execute(self) -> 'BaseResult':
        """执行选择流程，返回需要执行的动作列表。"""

        # 1) 基础选项（不含"返回菜单"）
        if len(self.options) == 1:
            if get_game_state().config.get("mode") != "human":
                action_list = self.options[0].actions
                return MultipleActionsResult(action_list)
            if bool(get_game_state().config.get("auto_select_single_option", False)):
                action_list = self.options[0].actions
                return MultipleActionsResult(action_list)
        if len(self.options) == 0:
            return MultipleActionsResult([])

        # 2) 若为人类玩家，追加"返回菜单"选项
        # menu_action 内部可选择 return，将当前 SelectAction 插回队首
        # todo
        from actions.menu import add_menu_option_if_human
        effective_options = add_menu_option_if_human(
            self.options,
            self,
        )

        # 3) 展示标题与选项（翻译 name）
        if bool(get_game_state().config.get("show_menu", True)):
            print(f"\n=== {self.title} ===")
            for i, option in enumerate(effective_options):
                print(f"{i+1}. {option.name}")

        # 4) AI 调试模式可自动选择第一项
        if effective_options and bool(get_game_state().config.get("debug", False)):
            action_list = effective_options[0].actions
            return MultipleActionsResult(action_list)

        # 5) 交互式选择
        while True:
            try:
                prompt = t(
                    "ui.select_prompt",
                    default=f"Choose (1-{len(effective_options)}): ",
                    count=len(effective_options),
                )
                option = int(input(prompt)) - 1
                if 0 <= option < len(effective_options):
                    action_list = effective_options[option].actions
                    return MultipleActionsResult(action_list)
                print(t("ui.invalid_option", default="Invalid option!"))
            except (ValueError, EOFError):
                print(t("ui.invalid_number", default="Please enter a valid number"))
