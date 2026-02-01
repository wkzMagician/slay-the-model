"""
Localization module for multi-language support.
"""
import os
from typing import Dict, Any
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

def t(key: str, default: str | None = None, **kwargs) -> str:
    """Translate a key. If key starts with '@', use the rest as key."""
    if key.startswith('@'):
        key = key[1:]
    trans = translations.get(current_language, {}).get(key)
    if trans is None:
        trans = default or key
    # Format with kwargs
    try:
        trans = trans.format(**kwargs)
    except (KeyError, ValueError):
        pass
    return trans