# 房间类型实现设计文档

本文档整理了 RestRoom、ShopRoom、TreasureRoom 三种房间类型的实现机制。

---

## 1. RestRoom（休息站点）

### 标准选项

#### 1. Rest（休息）
- **效果**：恢复30%的最大HP
- **特殊机制**：
  - 被以下遗物禁用（置灰）：Coffee Dripper, Mark of the Bloom
  - 在满血时仍可选择

#### 2. Smith（锻造）
- **效果**：升级一张卡牌
- **特殊机制**：
  - 被以下遗物禁用：Fusion Hammer
  - 如果所有卡牌都已升级，则置灰

#### 3. Recall（召回）
- **效果**：获得 Ruby Key
- **特殊机制**：
  - 仅在 Act 4 已揭示或之前已召回后才会出现
  - 每次运行只能召回一次

### 遗物修饰符（Relic Modifiers）

#### 1. Dream Catcher
- **效果**：休息后增加卡牌奖励屏幕（受卡牌奖励遗物影响）

#### 2. Regal Pillow
- **效果**：休息时额外恢复15 HP

### 特殊选项（Special Options）

以下三个遗物只能在同一次运行中拾取其中一个：

#### 1. Girya
- **选项**：Lift（举重）
- **效果**：获得1点Strength（最多3次使用）
- **说明**：每次举重获得1点Strength，可重复使用

#### 2. Peace Pipe
- **选项**：Toke（吸烟）
- **效果**：从卡组中移除一张卡牌
- **说明**：类似卡牌移除服务

#### 3. Shovel
- **选项**：Dig（挖掘）
- **效果**：获得一个随机遗物
- **说明**：随机获得一个遗物

### 其他交互

#### 1. Eternal Feather
- **效果**：进入休息站点时，每5张卡牌自动恢复3 HP
- **说明**：无需选择操作，自动触发

#### 2. Ancient Tea Set
- **效果**：离开休息站点后，下一场战斗第一回合获得额外2点Energy

---

## 2. ShopRoom（商店）

### 商品构成

#### 1. 彩色卡牌（5张）
- **组成**：2张攻击卡、2张技能卡、1张能力卡
- **折扣**：随机一张卡牌享受50%折扣
- **价格**：
  - Common: 45-55 金币（Ascension 16: 50-61）
  - Uncommon: 68-83 金币（Ascension 16: 75-91）
  - Rare: 135-165 金币（Ascension 16: 149-182）

#### 2. 无色卡牌（2张）
- **组成**：1张Uncommon无色卡、1张Rare无色卡
- **说明**：无色卡牌比普通卡牌贵20%
- **价格**：
  - Uncommon: 81-99 金币（Ascension 16: 89-109）
  - Rare: 162-198 金币（Ascension 16: 178-218）

#### 3. 药水（3瓶）
- **权重**：
  - Common: 65%
  - Uncommon: 25%
  - Rare: 10%
- **价格**：
  - Common: 48-53 金币（Ascension 16: 52-58）
  - Uncommon: 71-79 金币（Ascension 16: 79-87）
  - Rare: 95-105 金币（Ascension 16: 105-116）

#### 4. 遗物（3个）
- **说明**：最右侧槽位始终是商店遗物（Shop Relic），这是获取商店遗物的唯一方式
- **权重**：
  - Common: 50%
  - Uncommon: 33%
  - Rare: 17%
- **价格**：
  - Shop Relic: 143-158 金币（Ascension 16: 157-173）
  - Common Relic: 143-158 金币（Ascension 16: 157-173）
  - Uncommon Relic: 238-263 金币（Ascension 16: 261-289）
  - Rare Relic: 285-315 金币（Ascension 16: 314-347）

#### 5. 卡牌移除服务
- **价格**：起始75金币，每次购买后增加25金币
- **限制**：每家商店只能使用一次

### 遗物交互

#### 1. Smiling Mask
- **效果**：将卡牌移除服务价格永久设为50金币，且不再随使用次数增加

#### 2. Membership Card
- **效果**：所有商品价格降低50%

#### 3. Maw Bank
- **效果**：每层获得12金币，在商店花费金币后不再工作

#### 4. The Courier
- **效果**：
  - 购买的卡牌、遗物和药水会重新上架
  - 价格降低20%
  - **注意**：商店遗物（Shop Relics）不会重新上架
  - 重新上架的商品价格不受Ascension 16影响

#### 组合效果
- **The Courier + Membership Card**：
  - 总共降低60%价格（0.8 * 0.5 = 0.4）
  - 即价格为原价的40%

### Ascension 16效果
- 所有商品价格增加10%

---

## 3. TreasureRoom（宝箱房间）

### 宝箱类型

根据概率生成三种大小的宝箱：

#### 1. 小宝箱（50%概率）
- **遗物概率**：
  - Common: 75%
  - Uncommon: 25%
  - Rare: 0%
- **金币概率**：50%
- **金币数量**：23-27

#### 2. 中宝箱（33%概率）
- **遗物概率**：
  - Common: 35%
  - Uncommon: 50%
  - Rare: 15%
- **金币概率**：35%
- **金币数量**：45-55

#### 3. 大宝箱（17%概率）
- **遗物概率**：
  - Common: 0%
  - Uncommon: 75%
  - Rare: 25%
- **金币概率**：50%
- **金币数量**：68-82

### Boss宝箱

- **组成**：3个Boss遗物供选择
- **特点**：
  - 可以跳过奖励
  - 不符合标准宝箱的概率分布

### 相关遗物交互

#### 1. N'loth's Hungry Face
- **效果**：宝箱中不会出现Sapphire Key
- **说明**：替代了Sapphire Key的位置

#### 2. Cursed Key
- **效果**：未在获取的页面中找到详细信息，需要补充

#### 3. Matryoshka
- **效果**：Boss宝箱中的底部遗物变为另一个遗物
- **说明**：即Boss宝箱会包含4个遗物（3个选择+1个隐藏）

---

## 实现要点

### 1. RestRoom
- 实现3个标准选项的UI交互
- 处理遗物对选项的影响（Girya/Shovel/Peace Pipe）
- 支持Dream Catcher和Regal Pillow的自动效果
- 支持Eternal Feather和Ancient Tea Set的自动触发

### 2. ShopRoom
- 生成5张彩色卡、2张无色卡、3瓶药水、3个遗物
- 实现价格计算（考虑Ascension等级和遗物）
- 实现卡牌移除服务（每次价格递增）
- 处理The Courier的重新上架机制
- 处理各种遗物对价格的影响

### 3. TreasureRoom
- 根据概率随机生成小/中/大宝箱
- 根据宝箱类型决定遗物稀有度和金币
- Boss宝箱特殊处理（3个Boss遗物）
- 处理Matryoshka的额外遗物效果
- 处理N'loth's Hungry Face的Sapphire Key替换

### 4. 通用要求
- 与GameState集成（访问player、relics、deck等）
- 使用Option类提供用户交互选项
- 支持本地化（继承Localizable）
- 遵循项目的动作系统架构