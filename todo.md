# TODO 列表

## 概述
本文档汇总了项目中所有TODO注释（共40条），按类型和优先级分类。

## 分类说明

### 类型分类
- **机制未实现**：核心游戏机制缺失，阻塞关键功能
- **功能未完整**：某个功能部分实现，需要补充完整
- **特殊情况处理**：边缘情况或特殊情况的处理
- **数据结构优化**：数据结构需要改进或重构
- **提示/文档**：需要添加详细说明或文档

### 优先级分类
- **高优先级**：影响核心玩法或阻塞其他功能的实现
- **中优先级**：重要的游戏机制，但不阻塞基本流程
- **低优先级**：优化项或锦上添花的功能

---

## TODO 详细表格

| # | 位置 | TODO 内容 | 类型 | 优先级 | 说明 |
|---|------|----------|------|--------|------|
### 机制未实现（高优先级）
| 1 | `map/map_manager.py:138-141` | Get monster encounter from game state (For now, returning empty enemy list - requires encounter pool system) | 机制未实现 | 高 | 怪物遭遇池系统缺失，导致战斗房间无法正常生成怪物 |
| 2 | `map/map_manager.py:143-146` | Get elite encounter from game state (For now, returning empty enemy list) | 机制未实现 | 高 | 精英遭遇池系统缺失 |
| 3 | `map/map_manager.py:148-151` | Get boss encounter from game state | 机制未实现 | 高 | Boss遭遇池系统缺失 |
| 4 | `potions/watcher.py:36-37` | Implement stance selection (Note: This needs stance system implementation) | 机制未实现 | 高 | Watcher姿态系统缺失，阻塞Watcher相关功能 |
| 5 | `potions/watcher.py:46-47` | Implement Divinity stance entry (Note: This needs stance system implementation) | 机制未实现 | 高 | Watcher神性姿态缺失 |
| 6 | `relics/global/boss.py:22-24` | Create ConfusedPower and apply it here (Note: This needs stance system implementation) | 机制未实现 | 高 | 困惑状态缺失，阻塞Slaver enemies |
| 8 | `engine/combat.py:98` | Trigger combat start effects (relics) | 机制未实现 | 高 | 战斗开始时的遗物效果未触发 |

### 功能未完整（高优先级）
| 9 | `potions/global_potions.py:75-76` | Implement proper 2-step process (discard selection -> draw) | 功能未完整 | 高 | 抽牌药水需要先弃牌再抽牌的两步流程 |
| 10 | `potions/global_potions.py:82-83` | Implement proper escape action | 功能未完整 | 高 | 逃逸药水的逃逸逻辑未实现 |
| 11 | `potions/global_potions.py:108` | Implement card cost randomization | 功能未完整 | 高 | 随机费用药水未实现随机化逻辑 |
| 12 | `potions/global_potions.py:113` | Implement potion slot filling logic (Note: This needs to use channel_orb action) | 功能未完整 | 高 | 药水槽填充逻辑缺失 |
| 13 | `potions/defect.py:41-42` | Implement proper channel orb action (Note: This needs orb slot modification action) | 功能未完整 | 高 | Defect的法球投放动作未实现 |
| 14 | `potions/defect.py:52` | Implement orb slot gain action | 功能未完整 | 高 | 法球槽增加动作未实现 |
| 15 | `cards/ironclad/cards.py:41` | ApplyPowerAction, apply vulnerable to target | 功能未完整 | 高 | 脆弱效果应用未实现 |
| 16 | `actions/card.py:7` | 参数 card_type | 功能未完整 | 高 | 卡牌动作需要card_type参数支持 |

### 功能未完整（中优先级）
| 17 | `cards/ironclad/cards.py:66` | 重刃独特的力量加成 | 功能未完整 | 中 | 重刃卡牌的特殊力量加成逻辑 |
| 18 | `cards/ironclad/cards.py:79` | 攻击力等于防御力的逻辑在哪里实现？ | 功能未完整 | 中 | Body Slam卡牌的核心机制未实现 |
| 19 | `cards/base.py:91` | 调用util里的函数，更新self.temp_values | 功能未完整 | 中 | 卡牌临时值更新机制未实现 |
| 20 | `actions/combat.py:35` | 支持从抽牌堆打出牌 | 功能未完整 | 中 | 某些卡牌（如Limit Break）需要从抽牌堆打出 |
| 21 | `actions/combat.py:39` | 支持打出时无视费用 | 功能未完整 | 中 | 某些卡牌（如After Image）需要无视费用打出 |
| 22 | `engine/combat.py:71` | power tick_down | 功能未完整 | 中 | 状态效果回合递减逻辑 |
| 23 | `engine/combat.py:89` | modified by relics/powers | 功能未完整 | 中 | 初始抽牌数未考虑遗物/能力加成 |
| 24 | `player/status_manager.py:22` | 重新更新一系列数据，比如玩家手牌的攻击力，怪物的攻击力 | 功能未完整 | 中 | 状态变化后需要重新计算属性 |

### 数据结构优化（中优先级）
| 25 | `map/map_manager.py:52` | use relic's own counter | 数据结构优化 | 中 | Tiny Chest计数器应该由遗物自己管理 |
| 26 | `engine/combat.py:57` | Collection 数据结构 | 数据结构优化 | 中 | 药水/遗物管理需要更好的数据结构 |

### 特殊情况处理（中优先级）
| 27 | `rooms/combat.py:53` | 价格波动 | 特殊情况处理 | 中 | Boss房间应该有价格波动机制 |
| 28 | `potions/ironclad.py:28` | 当且Select只能单选，必须重复调用直到玩家选择Done | 特殊情况处理 | 中 | 多选卡牌药水需要循环Select直到Done |
| 29 | `actions/misc.py:18` | MawBank的逻辑 | 特殊情况处理 | 中 | MawBank遗物需要追踪花费金币 |
| 30 | `actions/display.py:68` | 若为人类玩家，追加"返回菜单"选项 | 特殊情况处理 | 中 | SelectAction需要返回菜单功能 |

### 提示/文档（低优先级）
| 31 | `engine/combat.py:40` | print combat information | 提示/文档 | 低 | 需要添加战斗信息打印 |
| 32 | `engine/combat.py:59` | 详细说明 | 提示/文档 | 低 | 药水ID需要更详细的说明 |
| 33 | `utils/random.py:11` | 对于没有指定稀有度的情况，考虑根据权重选择稀有度 | 提示/文档 | 低 | 随机卡牌稀有度选择逻辑 |
| 34 | `rooms/rest.py:39` | Recall option (Ruby Key) - disabled for now | 提示/文档 | 低 | Ruby Key重置功能未实现 |

### 当前回合费用为0（重复项，已合并）
| 35 | `potions/global_potions.py:42` | 当前回合费用为0 | 功能未完整 | 中 | Energy Potion药水需要设置本回合费用为0 |
| 36 | `potions/global_potions.py:50` | 当前回合费用为0 | 功能未完整 | 中 | 同上（重复） |
| 37 | `potions/global_potions.py:96` | 当前回合费用为0 | 功能未完整 | 中 | 同上（重复） |
| 38 | `potions/global_potions.py:102` | 当前回合费用为0 | 功能未完整 | 中 | 同上（重复） |

### 已解决/备注
| 39 | `relics/global/common.py:17` | 怎么应用攻击加成 | 提示/文档 | 低 | Bottle Flame遗物的攻击加成应用位置 |
| 40 | `rooms/rest.py:37-40` | Recall option (Ruby Key) | 特殊情况处理 | 低 | 已注释禁用，需要Ruby Key支持 |

---

## 统计汇总

### 按文件统计
| 文件 | TODO数量 |
|------|----------|
| potions/global_potions.py | 11 |
| engine/combat.py | 7 |
| map/map_manager.py | 4 |
| potions/watcher.py | 2 |
| potions/defect.py | 2 |
| cards/ironclad/cards.py | 4 |
| actions/ | 3 |
| 其他 | 7 |

### 按类型统计
| 类型 | 数量 | 占比 |
|------|------|------|
| 机制未实现 | 8 | 20% |
| 功能未完整 | 16 | 40% |
| 特殊情况处理 | 4 | 10% |
| 数据结构优化 | 2 | 5% |
| 提示/文档 | 10 | 25% |

### 按优先级统计
| 优先级 | 数量 | 占比 |
|--------|------|------|
| 高优先级 | 16 | 40% |
| 中优先级 | 14 | 35% |
| 低优先级 | 10 | 25% |

---

## 关键阻塞项说明

### 1. 遭遇池系统（高优先级）
**影响范围**：所有战斗房间
**阻塞项**：TODO #1, #2, #3
**说明**：怪物遭遇池系统未实现，导致战斗房间无法正常生成敌人。需要设计并实现：
- 普通遭遇池（按楼层划分）
- 精英遭遇池
- Boss遭遇池

### 2. 姿态系统（高优先级）
**影响范围**：Watcher角色、部分药水、Slaver enemies
**阻塞项**：TODO #4, #5, #6
**说明**：姿态系统未实现，阻塞：
- Watcher的三种姿态（Calm, Wrath, Divinity）
- 姿态切换药水（Watcher相关）
- Slaver的困惑效果（涉及姿态混乱）

### 4. 法球系统（高优先级）
**影响范围**：Defect角色、法球药水
**阻塞项**：TODO #13, #14
**说明**：法球投放和槽位管理未实现，阻塞Defect角色的核心机制。

### 5. Collection数据结构（中优先级）
**影响范围**：药水/遗物管理
**阻塞项**：TODO #26
**说明**：当前使用列表管理药水/遗物，需要更高效的数据结构支持：
- 快速查找
- 数量统计
- 唯一性检查

---

## 建议实施顺序

### 第一阶段：核心战斗系统
1. 遭遇池系统（TODO #1, #2, #3）
2. 战斗开始效果（TODO #8）

### 第二阶段：核心卡牌机制
4. 脆弱效果应用（TODO #15）
5. Body Slam攻击力等于防御力（TODO #18）
6. 卡牌临时值更新（TODO #19）
7. 支持从抽牌堆打出/无视费用（TODO #20, #21）

### 第三阶段：药水系统完善
8. 抽牌药水两步流程（TODO #9）
9. 逃逸药水（TODO #10）
10. 随机费用药水（TODO #11）
11. Energy Potion设置费用为0（TODO #35-38）
12. 药水槽填充（TODO #12）

### 第四阶段：角色系统
13. 姿态系统（TODO #4, #5, #6）
14. 法球系统（TODO #13, #14）
15. 重刃特殊加成（TODO #17）

### 第五阶段：优化和完善
16. Collection数据结构（TODO #26）
17. 状态变化属性更新（TODO #24）
18. power回合递减（TODO #22）
19. 特殊情况处理（TODO #27-30）
20. 文档和提示（TODO #31-34）