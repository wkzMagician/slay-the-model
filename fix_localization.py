#!/usr/bin/env python
"""
Localization Fix Script for Slay the Model

Analyzes res.txt (Chinese mode game output) to find English strings
and generates fixes for zh.yaml and Python source files.

Usage: python fix_localization.py
"""

import re
import os
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Project root
ROOT = Path(__file__).parent

# Load localization files
def load_yaml_keys(filepath: str) -> Set[str]:
    """Extract all keys from a YAML file (flattened)."""
    import yaml
    keys = set()
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}
        def flatten(d, prefix=''):
            for k, v in d.items():
                new_key = f"{prefix}.{k}" if prefix else k
                if isinstance(v, dict):
                    flatten(v, new_key)
                else:
                    keys.add(new_key)
        flatten(data)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
    return keys

en_keys = load_yaml_keys(ROOT / "localization" / "en.yaml")
zh_keys = load_yaml_keys(ROOT / "localization" / "zh.yaml")

# Find missing keys in zh.yaml
missing_in_zh = en_keys - zh_keys
print(f"=== Missing keys in zh.yaml ({len(missing_in_zh)}) ===")
for key in sorted(missing_in_zh):
    print(f"  - {key}")

# Analyze res.txt for English strings
res_file = ROOT / "res.txt"
if not res_file.exists():
    print(f"Error: {res_file} not found")
    exit(1)

with open(res_file, 'r', encoding='utf-8') as f:
    res_content = f.read()

# Patterns to detect English text in Chinese mode output
english_patterns = [
    # Neow dialogue
    (r"Welcome, traveler\. I am Neow\.", "ui.neo_welcome"),
    (r"I shall grant you a blessing", "ui.neo_intro"),
    (r"Your journey begins now", "ui.neo_goodbye"),
    (r"Max HP changed by", "ui.neo_max_hp_change"),
    
    # Map view
    (r"MAP VIEW - Act", "ui.map_view"),
    (r"Legend:", "ui.legend"),
    (r"\[M\]=Monster", "ui.legend_monster"),
    (r"\[E\]=Elite", "ui.legend_elite"),
    (r"\[\$\]=Merchant", "ui.legend_merchant"),
    (r"\[\?\]=Event", "ui.legend_event"),
    (r"\[R\]=Rest", "ui.legend_rest"),
    (r"\[T\]=Treasure", "ui.legend_treasure"),
    (r"\[B\]=Boss", "ui.legend_boss"),
    (r"\[N\]=Neo", "ui.legend_neo"),
    (r"\*=Current", "ui.legend_current"),
    (r">=Available", "ui.legend_available"),
    (r"\^=Visited", "ui.legend_visited"),
    (r"Connections:", "ui.connections"),
    (r"/=left", "ui.conn_left"),
    (r"\|=center", "ui.conn_center"),
    (r"\\=right", "ui.conn_right"),
    (r"Floor \d+:", "ui.floor_label"),
    
    # Combat
    (r"Draw Pile", "combat.draw_pile"),
    (r"Discard Pile", "combat.discard_pile"),
    (r"has been defeated!", "combat.enemy_defeated"),
    (r"\[Artifact\] Blocked debuff!", "combat.artifact_blocked"),
    (r"Remaining stacks:", "combat.artifact_remaining"),
    
    # Room options
    (r"rooms\.RestRoom\.RestRoom\.smith", "rooms.RestRoom.smith"),
    (r"rooms\.RestRoom\.RestRoom\.skip", "rooms.RestRoom.skip"),
    (r"rooms\.combat\.enter", "rooms.CombatRoom.enter"),
    
    # Shop/Potion
    (r"Rarity:", "ui.rarity_label"),
    (r"Category:", "ui.category_label"),
    (r"Type:", "ui.type_label"),
    (r"Duration:", "ui.duration_label"),
    (r"Amount:", "ui.amount_label"),
    
    # Power names (class references)
    (r"powers\.ArtifactPower\.name", "powers.ArtifactPower.name"),
    (r"Curl Up", "powers.CurlUpPower.name"),
    
    # Intention descriptions
    (r"enemies\.Cultist\.intentions\.attack\.description", "enemies.Cultist.intentions.attack.description"),
    
    # Unresolved placeholders
    (r"\{amount\}", "placeholder.amount"),
    (r"\{debuff\}", "placeholder.debuff"),
]

print("\n=== English strings found in res.txt ===")
issues_found = []
for pattern, key in english_patterns:
    matches = re.findall(pattern, res_content)
    if matches:
        count = len(matches)
        issues_found.append((key, pattern, count))
        print(f"  [{count}x] {key}: '{pattern}'")

# Check for hardcoded class references
class_ref_pattern = r'rooms\.\w+\.\w+\.\w+|powers\.\w+\.name|enemies\.\w+\.intentions\.\w+\.description'
class_refs = set(re.findall(class_ref_pattern, res_content))
if class_refs:
    print("\n=== Hardcoded class references (missing localization) ===")
    for ref in sorted(class_refs):
        print(f"  - {ref}")

# Generate zh.yaml additions
print("\n" + "="*60)
print("=== GENERATED zh.yaml ADDITIONS ===")
print("="*60)

zh_additions = """
# ===========================================
# MISSING UI KEYS (from en.yaml)
# ===========================================
ui:
  map_view: '地图 - 第 {act} 幕（第 {floor} 层）'
  legend: '图例:'
  legend_monster: '[M]=怪物'
  legend_elite: '[E]=精英'
  legend_merchant: '[$]=商店'
  legend_event: '[?]=事件'
  legend_rest: '[R]=休息'
  legend_treasure: '[T]=宝藏'
  legend_boss: '[B]=Boss'
  legend_neo: '[N]=捏奥'
  legend_current: '*=当前位置'
  legend_available: '>=可前往'
  legend_visited: '^=已访问'
  connections: '连接:'
  conn_left: '/=左'
  conn_center: '|=中'
  conn_right: '\\=右'
  floor_label: '第 {num} 层:'
  rarity_label: '稀有度: {rarity}'
  type_label: '类型: {type}'
  category_label: '类别: {category}'
  duration_label: '持续: {duration}'
  amount_label: '数量: {amount}'
  buff: 增益
  debuff: 减益
  permanent: 永久
  neo_welcome: 欢迎你，旅行者。我是捏奥。
  neo_intro: 我将赐予你一个祝福来开始你的旅程。
  neo_goodbye: 你的旅程现在开始。祝你好运！
  neo_max_hp_change: 最大生命值改变 {amount} 点！
  upgrade_comparison_header: '=== 升级前 ==='
  upgrade_comparison_separator: '\\n=== 升级后 ==='

# ===========================================
# MISSING COMBAT KEYS
# ===========================================
combat:
  draw_pile: 抽牌堆
  discard_pile: 弃牌堆
  enemy_defeated: '{enemy} 已被击败！'
  artifact_blocked: '[人工制品] 阻止了减益效果！'
  artifact_remaining: '剩余层数: {count}'

# ===========================================
# MISSING ROOMS SECTION
# ===========================================
rooms:
  RestRoom:
    title: 休息点
    rest: 休息（恢复 30% 生命值）
    smith: 锻造（升级一张卡牌）
    skip: 跳过
    lift: 举重（获得力量）
    toke: 吸烟（移除一张卡牌）
    dig: 挖掘（获得遗物）
    recall: 回忆（获得红宝石钥匙）
    enter: 你进入一个安静的休息点。
  CombatRoom:
    title: 战斗
    enter: === 战斗开始 ===
    victory: 胜利！所有敌人被击败！
  ShopRoom:
    title: 商店
    enter: 你进入了一个神秘的商店。
  TreasureRoom:
    title: 宝藏
    enter: 你发现了一个宝藏！
  EventRoom:
    title: 事件
    enter: 你遇到了一个事件。

# ===========================================
# MISSING POWER NAMES
# ===========================================
powers:
  ArtifactPower:
    name: 人工制品
    description: 阻止下次 {amount} 次受到的减益效果。
  CurlUpPower:
    name: 蜷身
    description: 受到伤害时获得 {amount} 点格挡。

# ===========================================
# MISSING ENEMY INTENTIONS
# ===========================================
enemies:
  Cultist:
    name: 邪教徒
    intentions:
      attack:
        description: 造成 {damage} 点伤害。
      ritual:
        description: 获得 {amount} 层仪式。
"""

print(zh_additions)

# Generate Python fixes
print("\n" + "="*60)
print("=== PYTHON SOURCE FILE FIXES NEEDED ===")
print("="*60)

python_fixes = """
# 1. map/map_manager.py - Replace hardcoded strings with t() calls
#    Line ~561: Change:
#      tui_print(f"MAP VIEW - Act {act_num} (Floor {current_floor})")
#    To:
#      tui_print(t("ui.map_view", act=act_num, floor=current_floor))
#
#    Line ~584-588: Replace hardcoded legend strings with t() calls

# 2. ai/context_builder.py - Lines ~171, 175
#    Change: "Draw Pile" -> t("combat.draw_pile")
#    Change: "Discard Pile" -> t("combat.discard_pile")

# 3. powers/definitions/artifact.py - Lines ~34-35
#    Change hardcoded "[Artifact] Blocked debuff!" messages to use t()

# 4. actions/combat.py - Line ~781
#    Change artifact message to use t("combat.artifact_blocked")

# 5. rooms/rest.py - Verify localization_prefix is correct
#    The code uses self.local("RestRoom.smith") with localization_prefix="rooms"
#    This creates key "rooms.RestRoom.smith" - need to add this to YAML
"""

print(python_fixes)

# Summary
print("\n" + "="*60)
print("=== SUMMARY ===")
print("="*60)
print(f"Total missing keys in zh.yaml: {len(missing_in_zh)}")
print(f"English patterns found in res.txt: {len(issues_found)}")
print(f"Hardcoded class references: {len(class_refs)}")
print("\nTo fix:")
print("1. Add the generated zh.yaml additions to localization/zh.yaml")
print("2. Update Python source files to use t() function")
print("3. Add missing localization keys to en.yaml if needed")
