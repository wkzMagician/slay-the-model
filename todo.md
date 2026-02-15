/ulw-loop 参考 @cards\ironclad\definations.md ，实现所有战士的卡牌。一些状态牌的定义在 @cards\colorsless\definations.md ，能力的定义在 @powers\buff.md @powers\debuff.md

/ulw-loop 参考 @cards\colorless\definations.md ，实现所有无色卡牌。一些已经实现的无色状态牌在 cards\colorless\ ，能力的定义在 @powers\buff.md @powers\debuff.md

/ulw-loop 参考 @relics\docs.md ，实现所有global和ironclad的遗物。已有的几个遗物实现在 relics\global_relics 和 relics\character\ 下。一些遗物通过on_xxx钩子生效，一部分通过施加能力生效，还有一部分，是在游戏流程中被引用（比如判断是否拥有该遗物）。能力的定义在 @powers\buff.md @powers\debuff.md。
Hint:
1. 主智能体负责实现遗物的代码。并向子智能体分配任务
2. 子智能体1负责从搜索引擎和网页中搜索指定遗物对应的描述，并返回主智能体。
3. 子智能体2负责搜索游戏项目中，游戏机制相关的代码，进行总结，并返回主智能体。
4. 子智能体3负责写这个遗物对应的测试代码，并负责运行测试代码，并把结果反馈给主智能体。

/ulw-loop 参考 @enemies\todo.md ，实现所有还没有实现的, act1怪物的类的相应意图。参考能力的定义在 @powers\buff.md @powers\debuff.md

/ulw-loop 参考 @powers\buff.md @powers\debuff.md，实现所有能力