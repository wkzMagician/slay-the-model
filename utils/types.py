from enum import Enum


class TargetType(str, Enum):
    SELF = "self"
    ENEMY_SELECT = "enemy_select"
    ENEMY_RANDOM = "enemy_random"
    ENEMY_LOWEST_HP = "enemy_lowest_hp"
    ENEMY_ALL = "enemy_all"

class PilePosType(str, Enum):
    TOP = "top"
    BOTTOM = "bottom"
    RANDOM = "random"

class StatusType(str, Enum):
    NEUTRAL = "Neutral"
    CALM = "Calm"
    WRATH = "Wrath"
    DIVINITY = "Divinity"
    
class CardType(str, Enum):
    ATTACK = "Attack"
    SKILL = "Skill"
    POWER = "Power"
    CURSE = "Curse"
    STATUS = "Status"
    
class RarityType(str, Enum):
    STARTER = "Starter"
    COMMON = "Common"
    UNCOMMON = "Uncommon"
    RARE = "Rare"
    SPECIAL = "Special"
    BOSS = "Boss"
    SHOP = "Shop"
    EVENT = "Event"
    BLIGHT = "Blight" 
    CURSE = "Curse"

class RoomType(str, Enum):
    NORMAL = "Normal"
    MONSTER = "Monster"
    ELITE = "Elite"
    REST = "Rest Site"
    MERCHANT = "Merchant"
    UNKNOWN = "Unknown"
    TREASURE = "Treasure"
    BOSS = "Boss"
    EVENT = "Event"
    NEO = "Neo"
    VICTORY = "Victory"

class CombatType(str, Enum):
    NORMAL = "Normal"
    ELITE = "Elite"
    BOSS = "Boss"

class EnemyType(str, Enum):
    NORMAL = "Normal"
    ELITE = "Elite"
    BOSS = "Boss"
    MINION = "Minion"


class DamageType(str, Enum):
    PHYSICAL = "physical"
    MAGICAL = "magical"
    HP_LOSS = "hp_loss"
