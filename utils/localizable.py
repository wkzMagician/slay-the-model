"""Localizable base class for unified name/description localization."""
from __future__ import annotations

from typing import Any
from localization import t


class Localizable:
    """Provide localized fields via prefix + class name."""

    localizable_fields: tuple[str, ...] = () # ("name", "description")
    localization_prefix: str = ""

    @property
    def localization_base_key(self) -> str:
        """返回形如 '{prefix}.{ClassName}' 的基础 key。"""
        base = self.__class__.__name__
        prefix = self.localization_prefix
        return f"{prefix}.{base}" if prefix else base

    def get_localized_key(self, field: str) -> str:
        """返回字段对应的本地化 key。"""
        return f"{self.localization_base_key}.{field}"

    def get_localized_value(self, field: str) -> str:
        """返回字段对应的本地化值。"""
        key = self.get_localized_key(field)
        return t(key, default="ERROR")
    
    def has_localized_key(self, field: str) -> bool:
        """检查是否存在字段对应的本地化 key。"""
        key = self.get_localized_key(field)
        localized_value = t(key, default=None)
        return localized_value is not None