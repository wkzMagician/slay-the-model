# TODO List

[] 拉去杀戮尖塔wiki中的所有内容，部分内容已经位于docs/下
    [] https://slay-the-spire.fandom.com/wiki/Slay_the_Spire_Wiki, 
    [] https://slaythespire.wiki.gg/
[] 对爬虫拉取的页面，进行清洗，整理出详细规整的markdown文档
[] 解决所有会导致 error warning 的地方，包括Typing检查错误的地方（即使程序可以正常运行）
[] 实现所有 todo
[] 新建MockRoom，模拟完整的游戏流程（从塔底爬到塔顶，胜利结束）
[] 实现战士的部分卡牌，所有starter，5common, 5uncommon, 5rare, 保证attack,skill,power 各>=3
    [] 相应，实现power
[] 实现战士所有遗物
[] 实现global的部分遗物，5common, 5uncommon, 5rare, 5boss, all-shop, 暂时没有event
[] 单独测试RestRoom （不考虑特殊遗物）
[] 单独测试TreasureRoom
[] 单独测试ShopRoom
[] 实现Enemy, 5个
[] 实现强怪、弱怪这些控制
[] 实现Combat逻辑
    [] 各各个action加上附加作用，比如ExhaustAction，触发各个power和relic的on_exhaust
    [] 实现回合制系统
    [] 默认选第一张牌，测试通过
[] 实现Event，5个
    [] 测试UnknownRoom