<div align="center">

# 🎮 Slay the Model

**A Framework for AI to Play Slay the Spire**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Stars](https://img.shields.io/github/stars/wkzMagician/slay-the-model.svg)](https://github.com/wkzMagician/slay-the-model/stargazers)

**English | [中文](README.md)**

</div>

---

### 📖 Introduction

**Slay the Model** is a Python-based framework that implements the core game mechanics of *Slay the Spire*, allowing AI models (such as DeepSeek, GPT, etc.) to play the game.

#### ✨ Key Features

- 🎯 **Complete Game Mechanics**: Card combat, relic system, potion system, event system, etc.
- 🤖 **AI Mode**: Support for LLM-based automatic game decision-making
- 🎮 **TUI Interface**: Modern terminal user interface based on Textual
- 🌍 **Localization**: Support for Chinese and English
- ⚙️ **Highly Configurable**: Customize game parameters via YAML config files

#### 🏗️ Project Structure

```
slay-the-model/
├── cards/          # Card system
├── enemies/        # Enemy definitions (by act)
├── relics/         # Relic system
├── potions/        # Potion system
├── powers/         # Power/buff/debuff system
├── events/         # Event system
├── engine/         # Game engine core
├── player/         # Player system
├── map/            # Map generation and management
├── rooms/          # Room types
├── tui/            # Terminal user interface
├── ai/             # AI interface
├── localization/   # Localization files
└── config/         # Configuration files
```

---

### 🔧 Environment Setup

#### Requirements

- Python 3.8 or higher
- Windows / macOS / Linux

#### Installation

1. **Clone the repository**
```bash
git clone https://github.com/wkzMagician/slay-the-model.git
cd slay-the-model
```

2. **Create virtual environment (recommended)**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

---

### ⚙️ Configuration

The configuration file is located at `config/game_config.yaml`. For first-time use, copy the template:

```bash
cp config/game_config_template.yaml config/game_config.yaml
```

#### Configuration Options

| Option | Description | Values |
|--------|-------------|--------|
| `mode` | Game mode | `human` (human control) / `ai` (AI control) / `debug` (debug mode) |
| `language` | Interface language | `zh` (Chinese) / `en` (English) |
| `seed` | Random seed | Any integer |
| `character` | Character | `Ironclad` (currently only Ironclad supported) |
| `ascension` | Ascension level | `0-20` (0 means no ascension) |

#### AI Mode Configuration

```yaml
ai:
  api_key: YOUR_API_KEY        # API key
  api_base: YOUR_MODEL_API_BASE # API endpoint
  model: YOUR_MODEL             # Model name
  stream: True                  # Stream output
  temperature: 0.7              # Temperature
  max_tokens: 8192             # Max tokens
  timeout: 60                   # Timeout (seconds)
```

#### Debug Mode Configuration

```yaml
debug:
  print: False          # Print debug info
  select_type: random   # Selection type: random / first
  god_mode: False       # God mode (enemies have 1 HP)
```

---

### 🚀 Running the Project

#### TUI Mode (Default, Recommended)

```bash
python __main__.py
```

#### CLI Mode (No UI)

```bash
python __main__.py --no-tui
```

---

### 📋 TODO

#### 🐛 Bug Fixes (High Priority)

- [ ] Fix localization display issues
- [ ] Improve error handling
- [ ] Verify and fix card effects
- [ ] Verify and fix relic effects
- [ ] Verify and fix potion effects
- [ ] Verify and fix power effects
- [ ] Verify and fix enemy behaviors/intentions

#### 🎮 Game Features (Medium Priority)

- [ ] Game mechanics changes at different ascension levels
- [ ] Three keys acquisition system
- [ ] Configuration for forced Act 4 entry

#### 🎮 Game Features (Low Priority)

- [ ] More quest systems
- [ ] Support for more characters (Silent, Defect, Watcher)

#### ✨ Features (High Priority)

- [ ] Support for local LLM deployment
- [ ] Improve documentation

#### ✨ Features (Medium Priority)

- [ ] Implement reinforcement learning framework
- [ ] Add more test cases

---

### 🎬 Demo

> 📹 Demo video coming soon...

---

### 🤝 Support Us

If this project helps you, please:

- ⭐ Star the project
- 🔄 Share with others
- 🐛 Submit Issues or PRs

#### Follow Us

📺 **Bilibili**: [wkzMagician](https://space.bilibili.com/)

---

<div align="center">

**Made with ❤️ by wkzMagician**

</div>