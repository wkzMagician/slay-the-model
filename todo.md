# TODO List

## 已完成的重构任务

### 架构重构

- [x] 重构GameFlow主循环
  - 从迭代action改为迭代room
  - 实现room-based的游戏循环
  - 支持room的init()和leave()生命周期

- [x] 重新定义Room基类接口
  - 每个Room有自己的action_queue
  - 实现init(), enter(), leave()方法
  - 实现execute_actions()辅助方法
  - 添加should_leave控制标志

- [x] 创建Combat类
  - 将战斗逻辑从CombatRoom中提取
  - 实现start()方法返回"WIN"/"DEATH"/None
  - 使用全局action_queue管理战斗操作

- [x] 重构CombatRoom
  - 使用新的Combat类
  - 只负责创建和执行Combat实例
  - 管理战斗后的奖励逻辑

- [x] 重构ShopRoom
  - 实现完整的商店逻辑
  - 内部构建action_queue
  - 使用LeaveShopAction控制离开

- [x] 重构其他Room类型
  - RestRoom: 实现休息选项
  - TreasureRoom: 实现宝箱开启
  - UnknownRoom: 实现房间/事件解析

- [x] 重构Event系统
  - 简化Event基类，移除EventStage
  - Event拥有自己的action_queue
  - Event只有trigger()方法
  - 添加CombatEvent基类

- [x] 重构UnknownRoom
  - 支持解析为其他Room类型
  - 支持解析为Event
  - 添加EVENT类型到RoomType

- [x] 调整GameState
  - 移除全局action_queue引用
  - 添加注释说明每个room/event有自己的queue

- [x] 更新所有Action以适配新架构
  - MoveToMapNodeAction: 只更新状态，不调用enter()
  - NeoEvent: 使用新的trigger()接口
  - NeoRewardRoom: 触发event并管理自身action_queue

## 待完成的任务

### 功能实现

- [ ] 实现Event池系统
  - 创建Event注册机制
  - UnknownRoom从池中随机选择Event
  - Event触发规则配置

- [ ] 完善Combat类
  - 实现完整的战斗流程
  - 回合管理
  - 卡牌系统集成
  - 敌人AI

- [ ] 完善RestRoom
  - 实现休息选项
  - 卡牌移除功能
  - 卡牌升级功能

- [ ] 完善ShopRoom
  - 商品生成逻辑
  - 价格计算
  - 卡牌移除服务

- [ ] 完善TreasureRoom
  - 宝箱类型系统
  - 奖励池配置
  - Boss宝箱特殊处理

### 测试

- [ ] 编写单元测试
  - 测试GameFlow主循环
  - 测试各种Room的enter/leave
  - 测试Event的trigger()
  - 测试Combat流程

- [ ] 集成测试
  - 测试完整的游戏流程
  - 测试房间转换
  - 测试战斗流程

### 文档

- [ ] 更新架构文档
  - 新的Room-based架构说明
  - Event系统说明
  - Combat类说明

- [ ] 添加代码注释
  - 关键类和方法添加docstring
  - 复杂逻辑添加行内注释

## 技术债务

- [ ] 移除旧的Event相关代码
  - 检查是否有旧的EventStage引用
  - 清理不再使用的类和方法

- [ ] 统一ActionQueue使用
  - 明确哪些使用全局queue
  - 明确哪些使用局部queue
  - 添加清晰的文档说明

## 未来改进

- [ ] 性能优化
  - 减少不必要的对象创建
  - 优化事件/房间数据结构

- [ ] 扩展性改进
  - 支持自定义房间类型
  - 支持自定义事件
  - 支持插件系统