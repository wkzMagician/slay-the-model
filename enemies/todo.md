# 关于怪物的一些机制介绍

## 怪物意图实例

### Jaw Worm

| Name   | Intent | Effect                                                                 |
|--------|--------|------------------------------------------------------------------------|
| Chomp  | ⚔️     | Deals 11 damage.<br>Deals 12 🔥2 damage.                                  |
| Bellow | 🔥     | Gains 3 Strength. Gains 6 Block.<br>Gains 4 🔥2 Strength. Gains 6 Block.<br>Gains 5 🔥17 Strength. Gains 9 🔥17 Block. |
| Thrash | ⛨     | Deals 7 damage. Gains 5 Block.                                          |

Always starts with ⚔️ Chomp. If it is found in Act 3, it starts with the effects of 🔥 Bellow, and for it's first action it has a 45% chance of starting with 🔥 Bellow, a 30% chance of ⛨ Thrash and a 25% chance of using ⚔️ Chomp

- After using ⚔️ Chomp, it has a 59% chance of using 🔥 Bellow and a 41% of ⛨ Thrash
- After using 🔥 Bellow, it has a 56% chance of using ⛨ Thrash and a 44% of using ⚔️ Chomp
- After using ⛨ Thrash, it has a 45% chance of using 🔥 Bellow, a 30% chance of using ⛨ Thrash and a 25% chance of using ⚔️ Chomp. Unless ⛨ Thrash has been used 2 turns in a row, then it has a 64% chance of using 🔥 Bellow, and a 36% of using ⚔️ Chomp

### Cultisi

| Name   | Intent | Effect                                                                 |
|--------|--------|------------------------------------------------------------------------|
| Chomp  | ⚔️     | Deals 11 damage.<br>Deals 12 🔥2 damage.                                  |
| Bellow | 🔥     | Gains 3 Strength. Gains 6 Block.<br>Gains 4 🔥2 Strength. Gains 6 Block.<br>Gains 5 🔥17 Strength. Gains 9 🔥17 Block. |
| Thrash | ⛨     | Deals 7 damage. Gains 5 Block.                                          |

Always starts with ⚔️ Chomp. If it is found in Act 3, it starts with the effects of 🔥 Bellow, and for it's first action it has a 45% chance of starting with 🔥 Bellow, a 30% chance of ⛨ Thrash and a 25% chance of using ⚔️ Chomp

- After using ⚔️ Chomp, it has a 59% chance of using 🔥 Bellow and a 41% of ⛨ Thrash
- After using 🔥 Bellow, it has a 56% chance of using ⛨ Thrash and a 44% of using ⚔️ Chomp
- After using ⛨ Thrash, it has a 45% chance of using 🔥 Bellow, a 30% chance of using ⛨ Thrash and a 25% chance of using ⚔️ Chomp. Unless ⛨ Thrash has been used 2 turns in a row, then it has a 64% chance of using 🔥 Bellow, and a 36% of using ⚔️ Chomp

### Spike Slime (L)

| Name          | Intent | Effect                                                                 |
|---------------|--------|------------------------------------------------------------------------|
| Lick          | 🐍     | Applies 2 💧 Frail.<br>Applies 3 🔥17 💧 Frail.                            |
| Flame Tackle  | 🦎     | Deals 16 damage. Adds 2 🟢 Slimed into your discard pile.<br>Deals 18 🔥2. Adds 2 🟢 Slimed into your discard pile. |
| Split         | ???    | Disappears and spawns 2 💀 Spike Slimes (M) with its current HP.            |

Has a 30% chance of using 🦎 Flame Tackle and a 70% chance of using 🐍 Lick. Cannot use the same move three times in a row.<br>On Ascension 🔥17, it cannot use 🐍 Lick twice in a row.<br>Once its HP reaches 50% or lower, its current Intent will be interrupted and changed to ??? Split.

## 意图类（Intention）

每一个意图类有一个execute函数，其返回一个List[Action]

## Enemy类机制详解

在Creature基础之上，包含几个字段：

current_intention
一个intentions字典，定义意图的名字和对应的Intention实体
一个history_intensions列表，存放已经执行过的intentions
一个determine_next_intention函数，根据一系列信息决定下一个意图。因素包括：
- 之前执行过的意图（例子：同一个intention不会连续触发，等等）
- 当前的floor（例子：大鳄虫在Act1和Act3意图不同）
- 进阶等级 （影响意图&数值）

一些触发器函数，on_xx。例子：当史莱姆被打到半血一下（on_damage_taken），当前意图会变为分裂
另一个例子，on_combat_start，一些敌人可能会获得一些Power