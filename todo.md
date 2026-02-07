# TODO List

[*] 检查每一个action, event, 还有room，返回类型是否都已经更改为ResultType。要求action的execute，event的trigger，room的enter等，返回值都是这个类型，并且必须用Type详细标出。最后要用Pylint检查
[*] 检查每一个action, event, room，如果还有残留的”WIN","DEATH"等字符串，也替换成相应的ResultType

[*] 把return_types.py从 "actions/" 移动到 "utils/"。更新其它所有引用 
[] 关于战斗的所有残余逻辑