from __future__ import annotations

from typing import Any

from cards.base import RawLocalStr


class _SafeFormatDict(dict[str, Any]):
    def __missing__(self, key: str) -> str:
        return "{" + key + "}"


class StaticTextMixin:
    """Provide inline text without editing localization YAML."""

    text_name: str = ""
    text_description: str = ""
    text_upgrade_description: str = ""
    text_combat_description: str = ""
    text_upgrade_combat_description: str = ""

    def _text_for_field(self, field: str) -> str:
        mapping = {
            "name": getattr(self, "text_name", ""),
            "description": getattr(self, "text_description", ""),
            "upgrade_description": getattr(self, "text_upgrade_description", ""),
            "combat_description": getattr(self, "text_combat_description", "") or getattr(self, "text_description", ""),
            "upgrade_combat_description": getattr(self, "text_upgrade_combat_description", "") or getattr(self, "text_upgrade_description", ""),
        }
        return mapping.get(field, "")

    def local(self, field: str, **kwargs: Any) -> RawLocalStr:
        template = self._text_for_field(field)
        if not template:
            return RawLocalStr("")
        try:
            return RawLocalStr(template.format_map(_SafeFormatDict(kwargs)))
        except Exception:
            return RawLocalStr(template)

    def has_local(self, field: str) -> bool:
        return bool(self._text_for_field(field))
