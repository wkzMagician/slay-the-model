from typing import List, TYPE_CHECKING
from localization import BaseLocalStr

if TYPE_CHECKING:
    from actions.base import Action


class Option:
    """表示一个可供选择的选项。

    参数：
        name (BaseLocalStr): 选项名称的本地化键
        actions (List[Action]): 选择此选项时执行的动作列表
        enabled (bool): 选项是否可选，默认为True
    """

    def __init__(self, name: BaseLocalStr, actions: List["Action"], enabled: bool = True):
        self.name = name
        self.actions = actions
        self.enabled = enabled
