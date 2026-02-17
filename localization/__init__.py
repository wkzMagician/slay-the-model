"""
Localization module for multi-language support.
"""
import os
from typing import Dict, Any, Tuple
import yaml

# Default language
DEFAULT_LANGUAGE = 'en'

# Translations loaded from YAML
translations: Dict[str, Dict[str, Any]] = {}

current_language = DEFAULT_LANGUAGE

def _load_all_translations():
    """Load all translation files from localization directory."""
    global translations
    translations.clear()
    localization_dir = os.path.dirname(__file__)
    for filename in os.listdir(localization_dir):
        if filename.endswith('.yaml'):
            lang = filename[:-5]  # Remove .yaml
            file_path = os.path.join(localization_dir, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    translations[lang] = _flatten_dict(data)
            except Exception as e:
                print(f"Error loading {file_path}: {e}")

def _flatten_dict(d, prefix=''):
    """Flatten nested dict to dotted keys."""
    result = {}
    for k, v in d.items():
        new_key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            result.update(_flatten_dict(v, new_key))
        else:
            result[new_key] = v
    return result

# Load translations on import
_load_all_translations()

def set_language(lang: str):
    """Set the current language."""
    global current_language
    if lang in translations:
        current_language = lang

def t(key: str, default: Any = None, **kwargs) -> str:
    """Translate a key."""
    trans = translations.get(current_language, {}).get(key)
    if trans is None:
        trans = default or key
    # Resolve BaseLocalStr first
    if isinstance(trans, BaseLocalStr):
        trans = trans.resolve()
    # Ensure trans is a string
    if not isinstance(trans, str):
        trans = str(trans)
    # Format with kwargs
    try:
        trans = trans.format(**kwargs)
    except (KeyError, ValueError):
        pass
    return trans

class BaseLocalStr:
    def resolve(self) -> str:
        raise NotImplementedError

    def __str__(self):
        return self.resolve()

    def __add__(self, other):
        return ConcatLocalStr(self, other)

    def __radd__(self, other):
        return ConcatLocalStr(other, self)
    
class ConcatLocalStr(BaseLocalStr):
    def __init__(self, left: Any, right: Any):
        self.left = left
        self.right = right

    def resolve(self) -> str:
        left_str = str(self.left) if not isinstance(self.left, BaseLocalStr) else self.left.resolve()
        right_str = str(self.right) if not isinstance(self.right, BaseLocalStr) else self.right.resolve()
        return left_str + right_str

class LocalStr(BaseLocalStr):
    def __init__(self, key: str, **kwargs: Any):
        self.key = key
        self.kwargs = kwargs

    def resolve(self) -> str:
        return t(self.key, **self.kwargs)
    
class Localizable:
    """Provide localized fields via prefix + class name."""

    localizable_fields: Tuple[str, ...] = () # ("name", "description")
    localization_prefix: str = ""
    
    @property
    def idstr(self) -> str:
        """返回类名作为 ID 字符串。"""
        return self.__class__.__name__
    
    def _get_localized_key(self, field: str) -> str:
        """构建字段对应的本地化 key。"""
        # Prefer self.name if available as a direct attribute (not a property).
        # This is for classes like Intention that set self.name = "stab" in __init__.
        # Enemy.name is a property that calls local(), so we must avoid it here.
        name = self.__dict__.get('name') if 'name' in self.__dict__ else None
        identifier = name or self.idstr
        return f"{self.localization_prefix}.{identifier}.{field}"

    def local(self, field: str, **kwargs: Any) -> LocalStr:
        """返回字段对应的本地化字符串对象。"""
        return LocalStr(key=self._get_localized_key(field), **kwargs)
    
    def has_local(self, field: str) -> bool:
        """检查是否存在字段对应的本地化 field。"""
        # 简单检查是否存在翻译
        key = self._get_localized_key(field)
        translated = t(key, default=None)
        return translated is not None and translated != key