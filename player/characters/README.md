# 角色系统扩展指南

本文档说明如何添加新角色并配置其初始属性、卡组、遗物等。

## 概述

角色系统采用配置驱动的方式，每个角色的定义都集中在 `player/characters/` 目录下。系统使用 `@register_character` 装饰器自动注册角色配置，使得添加新角色变得简单且类型安全。

## 核心组件

### 1. CharacterConfig 数据类

位置：`player/character_config.py`

定义角色的所有可配置属性：

- `name`: 角色内部标识符（小写，用于注册）
- `display_name`: 角色显示名称（首字母大写，用于UI显示）
- `max_hp`: 最大生命值
- `energy`: 每回合能量
- `gold`: 初始金币
- `deck`: 初始卡组ID列表
- `starting_relics`: 初始遗物类名列表
- `orb_slots`: 球槽位数量
- `potion_limit`: 药水携带上限
- `draw_count`: 每回合抽卡数量

### 2. 角色注册装饰器

```python
@register_character(
    name="ironclad",
    display_name="Ironclad",
    max_hp=80,
    energy=3,
    gold=99,
    deck=[...],
    starting_relics=[...],
    ...
)
class IroncladConfig:
    """角色配置的文档说明"""
    pass
```

## 添加新角色步骤

### 步骤1：创建角色配置文件

在 `player/characters/` 目录下创建新文件，例如 `player/characters/my_character.py`：

```python
"""My Character configuration."""
from player.character_config import register_character


@register_character(
    name="my_character",
    display_name="MyCharacter",
    max_hp=75,
    energy=3,
    gold=99,
    deck=[
        "my_character.strike",
        "my_character.strike",
        "my_character.strike",
        "my_character.strike",
        "my_character.strike",
        "my_character.defend",
        "my_character.defend",
        "my_character.defend",
        "my_character.defend",
        "my_character.special_card",
    ],
    starting_relics=[
        "MyStartingRelic",  # 必须是已注册的遗物类名
    ],
    orb_slots=1,
    potion_limit=3,
    draw_count=5,
)
class MyCharacterConfig:
    """My Character: 角色描述。

    Starting relic: My Starting Relic (遗物效果)
    Starting deck: 5 Strike, 4 Defend, 1 Special Card
    """
    pass
```

### 步骤2：添加角色卡牌

在 `cards/` 目录下创建角色专属卡牌目录和文件：

```
cards/
├── my_character/
│   ├── __init__.py
│   ├── strike.py
│   ├── defend.py
│   └── special_card.py
```

每个卡牌文件使用 `@register("card")` 装饰器：

```python
# cards/my_character/strike.py
from cards.base import Card, CardType, Target
from utils.registry import register


@register("card")
class Strike(Card):
    """Deal 6 damage."""
    
    def __init__(self):
        super().__init__(
            cost=1,
            type=CardType.ATTACK,
            target=Target.ENEMY
        )
```

### 步骤3：添加角色遗物（可选）

如果角色需要专属遗物：

```python
# relics/character/my_character.py
from relics.base import Relic
from utils.types import RarityType
from utils.registry import register


@register("relic")
class MyStartingRelic(Relic):
    """My Character starting relic: 遗物效果描述."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON

    def on_combat_start(self, player, entities):
        """战斗开始时的效果"""
        return []  # 返回要执行的动作列表
```

### 步骤4：更新卡牌命名空间

在 `cards/namespaces.py` 中添加命名空间映射：

```python
CHARACTER_NAMESPACES = {
    "Ironclad": "ironclad",
    "Silent": "silent",
    "Defect": "defect",
    "Watcher": "watcher",
    "MyCharacter": "my_character",  # 添加这一行
}

NAMESPACE_COLORS = {
    "ironclad": "Red",
    "silent": "Green", 
    "defect": "Blue",
    "watcher": "Purple",
    "my_character": "Yellow",  # 添加这一行
    ...
}
```

### 步骤5：导出新角色

在 `player/characters/__init__.py` 中添加导入：

```python
"""Character configurations package."""
import player.characters.ironclad  # noqa: F401
import player.characters.silent  # noqa: F401
import player.characters.my_character  # noqa: F401  # 添加这一行
```

## 使用示例

### 创建特定角色玩家

```python
from player.player_factory import create_player

# 创建 Ironclad 角色
player = create_player("Ironclad")
print(player.character)  # 输出: "Ironclad"
print(player.max_hp)  # 输出: 80
print(len(player.card_manager.deck))  # 输出: 10
print([r.__class__.__name__ for r in player.relics])  # 输出: ['BurningBlood']

# 创建 Silent 角色
player = create_player("Silent")
print(player.character)  # 输出: "Silent"
print(player.max_hp)  # 输出: 70
```

### 列出所有可用角色

```python
from player.player_factory import list_characters

available = list_characters()
print(available)  # 输出: ['Ironclad', 'Silent', 'MyCharacter']
```

### 使用默认角色（从配置文件）

```python
# 不传参数，使用 config/game_config.yaml 中的默认角色
player = create_player()
```

## 配置文件示例

### Ironclad 配置

```python
@register_character(
    name="ironclad",
    display_name="Ironclad",
    max_hp=80,          # 80 HP
    energy=3,            # 每回合 3 能量
    gold=99,             # 初始 99 金币
    deck=[
        "ironclad.strike", "ironclad.strike", "ironclad.strike",
        "ironclad.strike", "ironclad.strike",  # 5 张 Strike
        "ironclad.defend", "ironclad.defend", "ironclad.defend",
        "ironclad.defend",  # 4 张 Defend
        "ironclad.bash",  # 1 张 Bash
    ],
    starting_relics=["BurningBlood"],  # 燃烧之血
    orb_slots=1,          # 1 个球槽位
    potion_limit=3,        # 最多 3 瓶药水
    draw_count=5,          # 每回合抽 5 张牌
)
class IroncladConfig:
    """Ironclad: 战士角色，擅长力量和重击。

    Starting relic: Burning Blood (每次战斗结束后治疗 6 HP)
    Starting deck: 5 Strike, 4 Defend, 1 Bash
    """
    pass
```

### Silent 配置

```python
@register_character(
    name="silent",
    display_name="Silent",
    max_hp=70,          # 70 HP
    energy=3,            # 每回合 3 能量
    gold=99,             # 初始 99 金币
    deck=[
        "silent.strike", "silent.strike", "silent.strike",
        "silent.strike", "silent.strike",  # 5 张 Strike
        "silent.defend", "silent.defend", "silent.defend",
        "silent.defend",  # 4 张 Defend
        "silent.survivor",  # 1 张 Survivor
    ],
    starting_relics=["CeramicFish"],  # 临时占位符
    orb_slots=1,          # 1 个球槽位
    potion_limit=3,        # 最多 3 瓶药水
    draw_count=5,          # 每回合抽 5 张牌
)
class SilentConfig:
    """Silent: 猎人角色，擅长毒素、匕首和精准打击。

    Starting relic: Ring of the Snake (获得 1 敏捷)
    Starting deck: 5 Strike, 4 Defend, 1 Survivor
    """
    pass
```

## 设计原则

### 1. 配置与实现分离

- **配置**：在 `player/characters/` 中定义角色的静态属性
- **实现**：在 `cards/`、`relics/`、`powers/` 中实现具体的游戏机制

### 2. 使用注册系统

- 卡牌使用 `@register("card")` 装饰器，ID 如 `"ironclad.strike"`
- 遗物使用 `@register("relic")` 装饰器，ID 如 `"BurningBlood"`
- 角色使用 `@register_character(...)` 装饰器

### 3. 类型安全

- 所有配置参数都有明确的类型
- 使用 `CharacterConfig` 数据类确保配置正确性
- 错误的卡牌或遗物ID会在运行时抛出 `ValueError`

## 常见问题

### Q: 如何修改角色的初始HP？

A: 编辑对应角色的配置文件，修改 `max_hp` 参数：
```python
@register_character(
    name="ironclad",
    max_hp=100,  # 修改这里
    ...
)
```

### Q: 如何添加新角色？

A: 按照"添加新角色步骤"章节的5个步骤操作：
1. 创建配置文件
2. 添加卡牌
3. 添加遗物（可选）
4. 更新命名空间
5. 更新导入

### Q: 卡牌ID如何确定？

A: 卡牌ID由注册装饰器和模块路径决定：
- 文件位置：`cards/ironclad/strike.py`
- 类名：`Strike`
- 注册装饰器：`@register("card")`
- ID：`"ironclad.strike"`（命名空间.类名小写）

### Q: 遗物ID如何确定？

A: 遗物ID就是类名：
- 文件位置：`relics/character/ironclad.py`
- 类名：`BurningBlood`
- 注册装饰器：`@register("relic")`
- ID：`"BurningBlood"`（直接使用类名）

### Q: 如何测试新角色？

A: 使用 `create_player()` 函数创建角色并检查属性：
```python
from player.player_factory import create_player

player = create_player("MyCharacter")
print(f"Character: {player.character}")
print(f"HP: {player.max_hp}")
print(f"Energy: {player.energy}")
print(f"Gold: {player.gold}")
print(f"Deck: {[card.__class__.__name__ for card in player.card_manager.deck]}")
print(f"Relics: {[r.__class__.__name__ for r in player.relics]}")
```

## 扩展性优势

1. **零代码侵入**：添加新角色不需要修改核心游戏逻辑
2. **类型安全**：配置错误会在运行时被捕获
3. **易于测试**：可以独立测试每个角色的配置
4. **灵活组合**：可以轻松创建角色变体或模组
5. **模块化**：每个角色的代码完全独立，便于维护

## 相关文件

- `player/character_config.py` - 角色配置基类和注册系统
- `player/characters/` - 角色配置文件目录
- `player/player_factory.py` - 角色工厂，创建玩家实例
- `cards/namespaces.py` - 卡牌命名空间映射
- `utils/registry.py` - 统一注册系统