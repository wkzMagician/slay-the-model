from typing import List
from actions.base import Action
from localization import BaseLocalStr


class Option:
    """表示一个可供选择的选项。

    参数：
        name (BaseLocalStr): 选项名称的本地化键
        actions (List[Action]): 选择此选项时执行的动作列表
        enabled (bool): 选项是否可选，默认为True
    """

    def __init__(self, name: BaseLocalStr, actions: List[Action], enabled: bool = True):
        self.name = name
        self.actions = actions
        self.enabled = enabled