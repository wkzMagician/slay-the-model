[-] 关于矛盾战斗中的特殊机制：The player begins this elite combat with the Debuff Surrounded. This only serves as a telegraph for their Back Attack mechanic and does not actually add any damage bonus.
Smoke Bomb cannot be used while Surrounded

[-] 大bug: 很多Enemy的intention中莫名有self.enemy.calculate_damage之类的调用。实际上，根本不需要这个函数，直接传self.damage到AttackAction就可以了

[-] 大bug: AttackAction中已经存在了一个resolve_potential_damage的伤害修改器。然而现在在DealDamageAction里面，又有get_damage_dealt_modifier，逻辑重复。个人认为，应当统一在resolve_potential_damage && resolve_card_damage 里面处理 power 的 modify_damage_dealt 和 modify_get_damage_taken_multiplier 修正。并且还要区分好顺序：关于加减算的优先，乘除放到后面

[-] 原来卡牌/药水/遗物的攻击选中目标，要么直接从所有enemy里面选，要么从不是is_dead的enemy里面选。应该统一改为从hp>0的enemy里面选。（即如果enemy还存活，但是hp=0，也无法选中）

[-] 补全/修改逻辑：act的地图布局。现在的地图布局是符合act1和act2。在act3，在ancension<20时，floor_in_act=17的楼层是VictoryRoom而不是TreasureRoom；而ancension=20时，由于有双boss站，floor_in_act=16和17是两个BossRoom（boss不同），而floor_in_act=18才是VictoryRoom。这个VictoryRoom会判断，player是否拥有3把钥匙。若没有，则直接胜利；若有，则转换到act4。act4的地图布局很独特，只有InitialRoom(act3的VictoryRoom)->RestRoom->ShopRoom->CombatRoom(Elite)->CombatRoom(Boss)->VictoryRoom，到达最后就代表最终的胜利。至于ancension，在config中调整。

[] ApplyPower的问题。
1. 有些power只有duration有意义，amount没有意义。
2. 而有的power，其duration=-1（永久），靠amount指定效果。
3. 有的power，duration=-1, amount也没有意义。
4. 有的power则amount和duration都有意义。
5. 还有的power，其amount值和duration锚定在一起。
这个问题相当复杂。首先要分析所有power所属的类型，可以用Web的skill/mcp搜索官方定义，也可以在本地的powers/buff.md和powers/debuff.md中搜索。其次，要对ApplyPowerAction的定义进行分析，是否要进行修改。最后检查所有ApplyPowerAction调用。
又：关于堆叠。有些能力不能堆叠，且能重复存在；有的能力不能堆叠，且不能重复存在。有的能可以堆叠（所以不可能重复存在）。如果可以堆叠，对于上面5中情况，1-只堆叠duration;2-堆叠amount;3-不堆叠;4-这种情况很少。像Bomb，就不可堆叠，可重复；5-这种情况同步堆叠

[] 检查所有 cards
[] 检查所有 enemies
[] 检查所有 powers
[] 检查所有 relics
[] 检查游戏能够成功运行
[] 完善进阶功能
[] 钥匙获取以及是否随心模式
[] 战斗界面美观化
[] 接入ai接口进行测试