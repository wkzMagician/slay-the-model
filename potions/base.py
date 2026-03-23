import random
from typing import List, Optional
from actions.base import Action
from entities.creature import Creature
from localization import Localizable, t
from utils.types import RarityType, TargetType

class Potion(Localizable):
    localization_prefix = "potions"
    rarity = RarityType.COMMON
    category = "Global"
    can_be_used_actively = True  # Default: can be used actively, override if passive only
    target_type = TargetType.SELF  # Default: targets the player

    def __init__(self):
        self._amount = 0
    
    @property
    def amount(self) -> int:
        """If player has relic: Sacred Bark, potion effects are doubled"""
        from engine.game_state import game_state
        if game_state.player and any(relic.idstr == "SacredBark" for relic in game_state.player.relics):
            return self._amount * 2
        return self._amount

    def on_use(self, targets: List[Creature]) -> List[Action]:
        """Base use method to be overridden by specific potions.
        
        Args:
            targets: List of resolved targets (single or multiple based on target_type)
        
        Returns:
            List of actions to execute
        """
        return []
    
    def info(self):
        """Return a stable human-readable potion summary."""
        name = str(self.local("name")) if self.has_local("name") else self.__class__.__name__
        rarity = t("ui.rarity_label", "Rarity: {rarity}", rarity=self.rarity.value)
        category = t("ui.category_label", "Category: {category}", category=self.category)
        description = str(self._get_dynamic_description()).strip()

        lines = [f"{name} ({rarity})", category]
        if description:
            lines.append(description)
        return "\n".join(lines)
    
    def _get_dynamic_description(self):
        """
        鑾峰彇鑽按鎻忚堪骞跺姩鎬佹浛鎹㈠彉閲?
        
        Returns:
            鏇挎崲鍙橀噺鍚庣殑鎻忚堪鏂囨湰
        """
        # 妫€鏌ユ槸鍚︽湁鎻忚堪
        if not self.has_local("description"):
            from localization import LocalStr
            return LocalStr(key="")
        
        # 鏋勫缓鍙橀噺瀛楀吀
        variables = {}
        
        # 鍩虹鍙橀噺 - amount, damage, block, energy 绛?
        if hasattr(self, 'amount'):
            variables['amount'] = self.amount
        if hasattr(self, '_amount'):
            variables['damage'] = self.amount  # 鐖嗙偢鑽按绛変娇鐢?amount 浣滀负浼ゅ
            variables['block'] = self.amount  # 鏍兼尅鑽按
            variables['energy'] = self.amount  # 鑳介噺鑽按
        
        # 鐗规畩鍙橀噺
        if hasattr(self, '__class__'):
            class_name = self.__class__.__name__
            
            # 鐖嗙偢鑽按 - 浣跨敤 damage 鍙橀噺
            if class_name == "ExplosivePotion":
                variables['damage'] = self.amount
            
            # 鏍兼尅鑽按 - 浣跨敤 block 鍙橀噺
            elif class_name == "BlockPotion":
                variables['block'] = self.amount
            
            # 鑳介噺鑽按 - 浣跨敤 energy_gain 鍙橀噺
            elif class_name == "EnergyPotion":
                variables['energy_gain'] = self.amount
            
            # 鎶界墝鑽按 - 浣跨敤 amount 鍙橀噺琛ㄧず鎶界墝鏁?
            elif class_name == "SwiftPotion":
                variables['amount'] = self.amount
            
            # 鎭愭儳鑽按 - 浣跨敤 amount 鍜?duration 鍙橀噺
            elif class_name == "FearPotion":
                variables['amount'] = self.amount
                variables['duration'] = self.amount
            
            # 鐏劙鑽按 - 浣跨敤 damage 鍙橀噺
            elif class_name == "FirePotion":
                variables['damage'] = self.amount
            
            # 鍔涢噺鑽按 - 浣跨敤 amount 鍙橀噺
            elif class_name == "StrengthPotion":
                variables['amount'] = self.amount
            
            # 鏁忔嵎鑽按 - 浣跨敤 amount 鍙橀噺
            elif class_name == "DexterityPotion":
                variables['amount'] = self.amount
            
            # 璧屽緬閰块€?- 闇€瑕佺壒娈婂鐞嗭紝鍥犱负杩欎釜鑽按璁╃帺瀹堕€夋嫨寮冪墝
            elif class_name == "GamblersBrew":
                # 璧屽緬閰块€犵殑鎻忚堪涓嶉渶瑕佸姩鎬佸€?
                pass
            
            # 閭暀寰掕嵂姘?- 浣跨敤 amount 鍙橀噺
            elif class_name == "CultistPotion":
                variables['amount'] = self.amount
            
            # 閾佷箣蹇?- 浣跨敤 metallicize 鍙橀噺
            elif class_name == "HeartOfIron":
                variables['metallicize'] = self.amount
            
            # 铏氬急鑽按 - 浣跨敤 magic_number 鍙橀噺
            elif class_name == "WeakPotion":
                variables['magic_number'] = self.amount
            
            # 姣掕嵂姘?- 浣跨敤 magic_number 鍙橀噺
            elif class_name == "PoisonPotion":
                variables['magic_number'] = self.amount
            
            # 涓撴敞鑽按 - 浣跨敤 magic_number 鍙橀噺
            elif class_name == "FocusPotion":
                variables['magic_number'] = self.amount
        
        # 杩斿洖甯︽湁鏍煎紡鍖栧彉閲忕殑 LocalStr 瀵硅薄
        return self.local("description", **variables)


