# 战斗机制

## 概述

战斗是《Slay the Spire》的核心机制之一,通过回合制的卡牌游戏进行。

## 基本战斗规则

### 回合结构
1. **玩家回合**:
   - 抽取5张卡牌
   - 初始拥有3点能量
   - 使用卡牌消耗能量
   - 回合结束时弃牌手牌
   
2. **敌人回合**:
   - 根据意图执行行动
   - 优先级为最高意图的敌人

### 卡牌使用
- 每张卡牌有能量消耗
- 玩家需要平衡能量使用和效果收益
- 弃牌堆为空时,弃牌堆重新洗入抽牌堆

### 意图系统
- 敌人会显示下一个动作意图:
  - **攻击** - 显示造成伤害数值
  - **防御** - 显示获得格挡数值
  - **Buff/Debuff** - 显示状态效果
  - **特殊** - 显示特殊动作

## 战斗胜利

### 击败敌人
- 获得卡牌奖励(3选1)
- 获得金币
- 有几率获得药剂(精英战有药剂奖励)
- 精英战额外获得1个遗物

## 战斗关键词

### 主要卡牌类型
- **Attack (攻击)**: 五角边框,直接造成伤害,可能有额外效果
- **Skill (技能)**: 长方形边框,提供防御、Buff、Debuff等效果
- **Power (能力)**: 圆形边框,持续整个战斗,一次性效果
- **Status (状态)**: 长方形边框,战斗中加入,战斗结束移除
- **Curse (诅咒)**: 长方形边框,永久加入卡牌,需要专门移除

## Boss战机制

- 每幕结束时都有Boss战
- 击败Boss:
  - 将玩家生命值恢复到满
  - 提供3张稀有卡牌选择
  - 提供3个Boss遗物选择
  - 提供额外金币(90-110)
  - 提供1瓶药剂
- 说明: Boss旨在被满血状态击败

## 精英战特点
- 更强的敌人,有独特技能和效果
- 需要策略性应对
- 战胜后获得额外遗物奖励

## 资料来源

- [Slay the Spire Wiki - Gameplay](https://slay-the-spire.fandom.com/wiki/Gameplay)

Turns
Combat is turn-based: first the player takes a turn, then the enemy party takes a turn, then repeat. This continues until either the enemy or the player dies.

Player Turn
At the start of the player's turn, three things happen:

Energy is set to the base energy (default 3), and
A number of cards are drawn (default 5), and
Start-of-turn effects trigger.
The default behavior can be changed, typically by Relics (e.g. FusionHammer.png Fusion Hammer increases the base energy by 1; SneckoEye.png Snecko Eye increases the number of cards drawn per turn by 2).

During their turn, the player may play cards or drink Potions. Cards with an energy cost will subtract that energy from the total. All player actions are resolved immediately upon being performed.

When the player presses End Turn, two things happen:

End-of-turn effects trigger.
This generally resolves in the order relics -> buffs -> cards (e.g. Orichalcum.png Orichalcum will trigger before Icon PlatedArmor.png Plated Armor, which will trigger before CardIcon Status.png Burns).
Cards in hand are shuffled into the discard pile.
This will not occur with RunicPyramid.png Runic Pyramid or any cards that are Retained, unless they are cards with end-of-turn Effects like CardIcon Curse.png Regret or CardIcon Status.png Burn.
Cards with end-of-turn Effects can sometimes also be Retained at exactly 1 point: during the Map-Awakened.png Awakened One phase shift. If Awakened One's first phase is killed with an effect that takes place right after the player's turn ends, but before the enemy turn begins (Defect's LightningOrb.png  Lightning Orb passive or StoneCalendar.png Stone Calendar), cards that would normally be discarded like CardIcon Status.png Burn can be Retained.
Then the enemy party takes its turn.

Enemy Turn
Enemy actions during their turn are governed by their Intents, visible as floating symbols above their heads. In multi-enemy encounters, enemies always take actions from left to right.

战斗流程伪代码：

```python
while True:
    result = self.execute_player_phase()
    if result.return_type in ("COMBAT_WIN", "COMBAT_LOSE", "COMBAT_ESCAPE"):
        break
    result = self.execute_enemy_phase()
    if result.return_type in ("COMBAT_WIN", "COMBAT_LOSE", "COMBAT_ESCAPE"):
        break
```

玩家回合

```python
result = self.start_player_phase() -> {
    # gain energy
    # draw crads
    # trigger Start-of-turn effects
}

while current_phase = "player"
    # build SelectAction for player: including playing cards, using potions, ending turn ...

result = self.end_player_phase() -> {
    # End-of-turn effects trigger
    # Cards in hand are shuffled into the discard pile
}
```

敌人回合

```python
# dead enemies are previously removed from the list
for enemy in self.enemies:
    enemy.take_actions()
```

