<div align="center">

# 🎮 Slay the Model

**一个让 AI 玩《杀戮尖塔》的框架**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Stars](https://img.shields.io/github/stars/wkzMagician/slay-the-model.svg)](https://github.com/wkzMagician/slay-the-model/stargazers)

**[English](README_EN.md) | 中文**

</div>

---

### 📖 项目介绍

**Slay the Model** 是一个基于 Python 的框架，实现了《杀戮尖塔》(Slay the Spire) 的核心游戏机制，并允许 AI 模型（如 DeepSeek、GPT 等）来玩这款游戏。

#### ✨ 核心特性

- 🎯 **完整游戏机制**：实现卡牌战斗、遗物系统、药水系统、事件系统等
- 🤖 **AI 模式**：支持接入大语言模型自动进行游戏决策
- 🎮 **TUI 界面**：基于 Textual 的现代化终端用户界面
- 🌍 **本地化支持**：支持中英文切换
- ⚙️ **高度可配置**：通过 YAML 配置文件自定义游戏参数

#### 🏗️ 项目结构

```
slay-the-model/
├── cards/          # 卡牌系统
├── enemies/        # 敌人定义（按章节分类）
├── relics/         # 遗物系统
├── potions/        # 药水系统
├── powers/         # 能力/buff/debuff 系统
├── events/         # 事件系统
├── engine/         # 游戏引擎核心
├── player/         # 玩家系统
├── map/            # 地图生成与管理
├── rooms/          # 房间类型
├── tui/            # 终端用户界面
├── ai/             # AI 接口
├── localization/   # 本地化文件
└── config/         # 配置文件
```

---

### 🔧 环境配置

#### 系统要求

- Python 3.8 或更高版本
- Windows / macOS / Linux

#### 安装步骤

1. **克隆仓库**
```bash
git clone https://github.com/wkzMagician/slay-the-model.git
cd slay-the-model
```

2. **创建虚拟环境（推荐）**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

---

### ⚙️ 配置说明

配置文件位于 `config/game_config.yaml`。首次使用时，请复制模板：

```bash
cp config/game_config_template.yaml config/game_config.yaml
```

#### 配置项说明

| 配置项 | 说明 | 可选值 |
|--------|------|--------|
| `mode` | 游戏模式 | `human` (人类控制) / `ai` (AI控制) / `debug` (调试模式) |
| `language` | 界面语言 | `zh` (中文) / `en` (英文) |
| `seed` | 随机种子 | 任意整数 |
| `character` | 角色 | `Ironclad` (目前仅支持铁甲战士) |
| `ascension` | 进阶等级 | `0-20` (0表示无进阶) |

#### AI 模式配置

```yaml
ai:
  api_key: YOUR_API_KEY        # API 密钥
  api_base: YOUR_MODEL_API_BASE # API 地址
  model: YOUR_MODEL             # 模型名称
  stream: True                  # 是否流式输出
  temperature: 0.7              # 温度参数
  max_tokens: 8192             # 最大 token 数
  timeout: 60                   # 超时时间（秒）
```

#### 调试模式配置

```yaml
debug:
  print: False          # 是否打印调试信息
  select_type: random   # 选择方式: random / first
  god_mode: False       # 上帝模式（敌人1血）
```

---

### 🚀 运行项目

#### TUI 模式（默认，推荐）

```bash
python __main__.py
```

#### CLI 模式（无界面）

```bash
python __main__.py --no-tui
```

---

### 📋 TODO

#### 🐛 Bug 修复 (High Priority)

- [ ] 本地化显示问题修复
- [ ] 错误处理优化
- [ ] 卡牌效果校对与修复
- [ ] 遗物效果校对与修复
- [ ] 药水效果校对与修复
- [ ] 能力（Power）效果校对与修复
- [ ] 敌人行为/意图校对与修复

#### 🎮 游戏功能补充 (Medium Priority)

- [ ] 不同进阶等级下的游戏机制变化
- [ ] 三把钥匙获取系统
- [ ] 是否强制进入 Act 4 的配置

#### 🎮 游戏功能补充 (Low Priority)

- [ ] 更多任务系统
- [ ] 更多角色支持（Silent、Defect、Watcher）

#### ✨ Feature (High Priority)

- [ ] 支持本地部署 LLM
- [ ] 完善文档

#### ✨ Feature (Medium Priority)

- [ ] 实现强化学习框架
- [ ] 添加更多测试用例

---

### 🎬 演示 Demo

> 📹 演示视频即将上线...

---

### 🤝 支持我们

如果这个项目对你有帮助，欢迎：

- ⭐ 给项目点个 Star
- 🔄 分享给更多人
- 🐛 提交 Issue 或 PR

#### 关注我们

📺 **Bilibili**: [wkzMagician](https://space.bilibili.com/)

---

<div align="center">

**Made with ❤️ by wkzMagician**

</div>