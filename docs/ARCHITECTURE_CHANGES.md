# 架构重构说明文档

## 概述

本次重构将游戏的主循环从"迭代action"改为"迭代room"，实现了更好的关注点分离和模块化。

## 核心变更

### 1. GameFlow 主循环重构

**旧架构：**
```python
while not game_over:
    action = action_queue.get_next()
    result = action.execute()
    # 处理各种action...
```

**新架构：**
```python
while current_floor < MAX_FLOOR:
    cur_room = map_select()
    cur_room.init()
    res = cur_room.enter()
    if res in ("DEATH", "WIN"):
        break
    cur_room.leave()
```

#### GameFlow 类接口变更

```python
class GameFlow:
    """Room-based游戏流控制器"""
    
    MAX_FLOOR = 16  # 最大层数
    
    def start_game(self):
        """启动游戏并运行主room循环"""
        # 1. 显示欢迎信息
        # 2. 初始化地图
        # 3. 开始Neo房间
        # 4. 主循环：迭代各个room
        #    - 选择下一个room
        #    - 初始化room
        #    - 进入room (room管理自己的action_queue)
        #    - 检查游戏结束条件
        #    - 离开room
    
    def _start_neo_room(self):
        """启动Neo奖励房间"""
        
    def _select_next_room(self):
        """从地图选择下一个room"""
        
    def _handle_game_over(self):
        """处理玩家死亡"""
        
    def _handle_game_won(self):
        """处理玩家胜利"""
```

### 2. Room 基类重新定义

#### Room 基类

```python
class Room(Localizable):
    """Room基类 - 每个room管理自己的action_queue和生命周期"""
    
    # 实例字段
    kwargs: dict              # 构造参数
    action_queue: ActionQueue  # Room专属的action队列
    should_leave: bool         # 离开标志，控制room内循环
    room_type: RoomType       # Room类型
    
    # 接口方法
    def init(self):
        """
        初始化room - 在enter()之前调用
        
        子类应该重写此方法以执行room特定的初始化
        例如：生成物品、敌人等
        """
        pass
    
    def enter(self) -> str:
        """
        进入room并执行room逻辑
        
        子类必须实现此方法
        应该实现room的主逻辑循环，根据需要构建和执行actions
        
        Returns:
            执行结果: None/"DEATH"/"WIN"
        """
        raise NotImplementedError()
    
    def leave(self):
        """
        离开room - 执行清理工作
        
        当玩家退出room时调用
        清除action_queue并准备进入下一个room
        """
        self.action_queue.clear()
        game_state.event_stack.clear()
        self.should_leave = False
    
    def execute_actions(self) -> str:
        """
        执行room的action_queue中的所有actions
        
        这是一个辅助方法，供room使用
        当should_leave为True或队列为空时停止执行
        
        Returns:
            执行结果（如果遇到特殊值），否则返回None
        """
        while not self.should_leave and not self.action_queue.is_empty():
            result = self.action_queue.execute_next()
            if result in ("DEATH", "WIN"):
                return result
        return None
```

#### UnknownRoom 特殊实现

```python
class UnknownRoom(Room):
    """Unknown房间 - 进入时解析为实际的room类型或event"""
    
    # 额外字段
    actual_room: Room    # 解析后的Room实例
    event: Event        # 或解析为Event实例
    
    def init(self):
        """初始化并解析room类型"""
        room_type = self._resolve_room_type()
        if room_type == RoomType.EVENT:
            self.event = self._create_event()
        else:
            self.actual_room = self._create_room(room_type)
            self.actual_room.init()
    
    def enter(self) -> str:
        """进入解析后的room或event"""
        if self.event:
            return self._execute_event()
        elif self.actual_room:
            return self.actual_room.enter()
        return None
    
    def _resolve_room_type(self) -> RoomType:
        """确定此unknown room的实际类型"""
        
    def _create_event(self):
        """创建随机event"""
        
    def _create_room(self, room_type: RoomType) -> Room:
        """创建指定类型的room实例"""
        
    def _execute_event(self) -> str:
        """执行event逻辑"""
```

### 3. Combat 类创建

```python
class Combat:
    """
    战斗逻辑控制器
    
    战斗逻辑从CombatRoom中提取到此独立类
    CombatRoom只负责创建和执行Combat实例
    """
    
    # 构造函数
    def __init__(self, enemies=None, is_elite=False):
        """
        Args:
            enemies: 敌人列表
            is_elite: 是否为精英战斗
        """
        self.enemies = enemies
        self.is_elite = is_elite
        # ... 其他战斗初始化
    
    def start(self) -> str:
        """
        开始战斗
        
        Returns:
            "WIN" - 玩家胜利
            "DEATH" - 玩家死亡
            None - 战斗意外结束（通常不会发生）
        """
        # 1. 初始化战斗
        # 2. 战斗主循环
        # 3. 处理结果
        pass
    
    def _initialize_combat(self):
        """初始化战斗状态"""
        
    def _combat_loop(self):
        """战斗主循环"""
        
    def _handle_victory(self):
        """处理胜利逻辑"""
        
    def _handle_defeat(self):
        """处理失败逻辑"""
```

### 4. CombatRoom 简化

```python
class CombatRoom(Room):
    """战斗房间 - 管理Combat的创建和执行"""
    
    # 字段
    combat: Combat      # Combat实例
    
    def init(self):
        """初始化战斗房间"""
        # 创建Combat实例
        pass
    
    def enter(self) -> str:
        """进入战斗房间"""
        # 执行Combat
        result = self.combat.start()
        
        if result == "WIN":
            # 处理奖励
            self._handle_rewards()
            self.should_leave = True
        elif result == "DEATH":
            pass  # Death handled by game flow
        
        return result
    
    def _handle_rewards(self):
        """处理战斗后奖励"""
```

### 5. ShopRoom 实现

```python
class ShopRoom(Room):
    """商店房间"""
    
    # 字段
    items: List[Item]       # 可购买物品
    cards: List[Card]       # 可购买卡牌
    purge_price: int        # 移除卡牌价格
    
    def init(self):
        """初始化商店"""
        # 生成商品
        pass
    
    def enter(self) -> str:
        """进入商店"""
        while not self.should_leave:
            # 构建商店菜单
            self._build_shop_menu()
            # 执行actions
            result = self.execute_actions()
            if result in ("DEATH", "WIN"):
                return result
        return None
    
    def _build_shop_menu(self):
        """构建商店菜单"""
        options = []
        # 添加购买选项
        # 添加离开选项
        self.action_queue.add_action(SelectAction(...))
```

### 6. Event 系统简化

#### Event 基类

```python
class Event(Localizable):
    """
    Event基类 - 代表Unknown Room中的随机事件
    
    Event拥有自己的action_queue
    只有一个trigger()方法用于触发和执行event
    """
    
    # 字段
    kwargs: dict              # 构造参数
    action_queue: ActionQueue  # Event专属的action队列
    event_ended: bool        # Event结束标志
    
    # 接口方法
    def trigger(self) -> str:
        """
        触发并执行event
        
        子类必须实现此方法
        应该实现event的主逻辑，构建和执行actions
        
        Returns:
            执行结果: None/"DEATH"/"WIN"
        """
        raise NotImplementedError()
    
    def execute_actions(self) -> str:
        """
        执行event的action_queue中的所有actions
        
        辅助方法，供event使用
        
        Returns:
            执行结果（如果遇到特殊值），否则返回None
        """
        while not self.event_ended and not self.action_queue.is_empty():
            result = self.action_queue.execute_next()
            if result in ("DEATH", "WIN"):
                return result
        return None
    
    def end_event(self) -> None:
        """结束event并返回到room流程"""
        self.event_ended = True
```

#### CombatEvent 基类

```python
class CombatEvent(Event):
    """
    CombatEvent基类 - 触发战斗的event
    
    这些event会进入战斗 encounter，然后返回正常游戏流程
    """
    
    # 额外字段
    enemies: List[Enemy]  # 敌人列表
    is_elite: bool       # 是否为精英
    
    def trigger(self) -> str:
        """触发战斗event"""
        # 1. 显示event描述
        # 2. 创建并启动Combat
        # 3. 处理战斗结果
        pass
    
    def _handle_victory(self):
        """处理战斗胜利 - 子类可重写以添加自定义奖励"""
        pass
```

#### NeoEvent 示例

```python
class NeoEvent(Event):
    """Neo祝福event - 特殊的起始event"""
    
    def trigger(self) -> str:
        """触发Neo祝福选择"""
        # 1. 显示欢迎消息
        # 2. 根据玩家历史显示不同的选项
        # 3. 执行actions
        # 4. 结束event
        result = self.execute_actions()
        self.end_event()
        return result
```

### 7. RoomType 枚举扩展

```python
class RoomType(str, Enum):
    MONSTER = "Monster"
    ELITE = "Elite"
    REST = "Rest Site"
    MERCHANT = "Merchant"
    UNKNOWN = "Unknown"
    TREASURE = "Treasure"
    BOSS = "Boss"
    EVENT = "Event"  # 新增
```

### 8. GameState 调整

```python
class GameState:
    """全局游戏状态"""
    
    # 移除的字段
    # action_queue: ActionQueue  # 已移除
    
    # 保留的字段
    map_manager: MapManager
    current_floor: int
    current_room: Room
    event_stack: List[Event]
    game_phase: str
    
    # 注意
    # action_queue不再在game_state中
    # 每个room/event现在有自己的action_queue
```

### 9. Action 调整

#### MoveToMapNodeAction

```python
class MoveToMapNodeAction(Action):
    """移动到特定地图节点"""
    
    # 参数
    floor: int       # 目标层数
    position: int   # 目标位置
    
    def execute(self):
        """
        执行移动
        
        注意：新架构下，此action只更新游戏状态
        room的enter()由GameFlow主循环调用，不由此action调用
        """
        # 移动到指定节点
        new_room = map_manager.move_to_node(floor, position)
        game_state.current_room = new_room
        game_state.current_floor = floor
```

#### LeaveXxxAction 模式

每个room类型应该有自己的LeaveXxxAction：

```python
class LeaveShopAction:
    """离开商店的action"""
    def execute(self):
        """设置should_leave标志"""
        room = game_state.current_room
        if isinstance(room, ShopRoom):
            room.should_leave = True

class LeaveRestAction:
    """离开休息点的action"""
    def execute(self):
        room = game_state.current_room
        if isinstance(room, RestRoom):
            room.should_leave = True
```

### 10. ActionQueue 使用说明

```python
# 全局action_queue (actions.base.action_queue)
# - 仍然存在
# - 用于Combat
# - 用于需要在全局上下文中执行的actions

# Room专属action_queue (Room.action_queue)
# - 每个Room实例有自己的action_queue
# - 用于room特定的actions
# - 在room.leave()时清空

# Event专属action_queue (Event.action_queue)
# - 每个Event实例有自己的action_queue
# - 用于event特定的actions
# - 在event结束后清空
```

## 架构优势

### 1. 关注点分离
- 每个Room管理自己的逻辑和状态
- 战斗逻辑独立于Room管理
- Event系统简化，更易于扩展

### 2. 模块化
- Room、Event、Combat都是独立的模块
- 可以单独测试每个模块
- 易于添加新的Room或Event类型

### 3. 代码复用
- Combat可以被CombatRoom和CombatEvent使用
- 基类提供了通用的接口和辅助方法
- Action可以在不同上下文中复用

### 4. 可维护性
- 清晰的生命周期 (init -> enter -> leave)
- 明确的职责划分
- 易于理解和修改

## 迁移指南

### 旧的Room实现模式

```python
class OldRoom(Room):
    def enter_room(self):
        # 直接使用全局action_queue
        action_queue.add_action(SomeAction())
        action_queue.execute_all()
```

### 新的Room实现模式

```python
class NewRoom(Room):
    def enter(self) -> str:
        # 使用自己的action_queue
        while not self.should_leave:
            # 构建菜单
            self.action_queue.add_action(SelectAction(...))
            # 执行actions
            result = self.execute_actions()
            if result in ("DEATH", "WIN"):
                return result
        return None
```

## 待实现功能

1. **Event池系统**
   - 创建Event注册机制
   - UnknownRoom从池中随机选择Event
   - Event触发规则配置

2. **完善Combat类**
   - 实现完整的战斗流程
   - 回合管理
   - 卡牌系统集成
   - 敌人AI

3. **完善各Room类型**
   - RestRoom: 休息、卡牌移除、升级
   - ShopRoom: 商品生成、价格计算
   - TreasureRoom: 宝箱类型、奖励池

## 测试建议

1. **单元测试**
   - 测试GameFlow主循环
   - 测试各种Room的enter/leave
   - 测试Event的trigger()
   - 测试Combat流程

2. **集成测试**
   - 测试完整的游戏流程
   - 测试房间转换
   - 测试战斗流程

## 总结

本次重构实现了以下目标：

1. ✓ 主循环从迭代action改为迭代room
2. ✓ action_queue在room内部构建
3. ✓ Event定义简化，移除EventStage
4. ✓ Combat逻辑独立在Combat类
5. ✓ 架构保持一致性，可以复用

新的架构更加清晰、模块化，便于后续扩展和维护。