import yaml
import os
from utils.seed import encode_seed, parse_seed_code

class GameConfig:
    def __init__(self, **kwargs):
        # Set default values matching game_config.yaml structure
        defaults = {
            "mode": "debug",
            "language": "en",
            "seed": -1,
            "character": "Ironclad",
            "ascension": 0,
            "daily_run": False,
            "highest_unlocked_ascension": {},
            "select_overflow": "truncate",
            "auto_select": False,  # Auto select for all modes (human, ai, debug)
            "human": {
                "show_menu_option": True,
            },
            "ai": {
                "api_key": os.environ.get("OPENAI_API_KEY", ""),
                "api_base": "https://api.openai.com/v1",
                "model": "gpt-4o",
                "stream": False,
                "temperature": 0.7,
                "max_tokens": 2048,
                "timeout": 60,
            },
            "debug": {
                "print": False,
                "select_type": "random",
                "god_mode": False,
            },
        }

        # Deep merge for nested configs
        for key, value in kwargs.items():
            if key in defaults and isinstance(defaults[key], dict) and isinstance(value, dict):
                defaults[key] = {**defaults[key], **value}
            else:
                defaults[key] = value

        # Set attributes explicitly
        self.mode = defaults["mode"]
        self.language = defaults["language"]
        legacy_seed = defaults["seed"]
        code = defaults.get("seed_code")
        if code is not None:
            if legacy_seed != -1:
                raise ValueError("Specify either seed_code or seed, not both")
            parsed = parse_seed_code(code)
        elif isinstance(legacy_seed, str):
            parsed = parse_seed_code(legacy_seed)
        elif type(legacy_seed) is int and -(1 << 63) <= legacy_seed < (1 << 63):
            parsed = None if legacy_seed == -1 else legacy_seed
        else:
            raise ValueError("seed must be a signed 64-bit integer or a seed code string")
        self.seed: int = parsed if parsed is not None else -1
        self.seed_specified: bool = parsed is not None
        self.seed_code: str = (encode_seed(parsed) or "0") if parsed is not None else ""
        self._seed_resolved: bool = parsed is not None
        self.character = defaults["character"]
        self.ascension = defaults["ascension"]
        self.daily_run = bool(defaults["daily_run"])
        self.highest_unlocked_ascension = {
            str(character).lower(): int(level)
            for character, level in defaults["highest_unlocked_ascension"].items()
        }
        self.select_overflow = defaults["select_overflow"]
        self.auto_select = defaults["auto_select"]
        self.human = defaults["human"]
        self.ai = defaults["ai"]
        self.debug = defaults["debug"]

    def resolve_seed(self, automatic_seed: int) -> None:
        """Resolve automatic seeds once while retaining their automatic identity."""
        if not self._seed_resolved:
            if type(automatic_seed) is not int or not -(1 << 63) <= automatic_seed < (1 << 63):
                raise ValueError("Automatic seed must be a signed 64-bit integer")
            self.seed = automatic_seed
            self.seed_code = encode_seed(automatic_seed) or "0"
            self._seed_resolved = True

    def get(self, key, default=None):
        """Dict-like access for compatibility with config.get usage.

        Supports nested access via dot notation: get("human.auto_select")
        """
        if "." in key:
            parts = key.split(".", 1)
            first = getattr(self, parts[0], None)
            if first is None:
                return default
            if isinstance(first, dict):
                return first.get(parts[1], default)
            return getattr(first, parts[1], default)
        return getattr(self, key, default)

    @staticmethod
    def load(config_path):
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8-sig") as f:
                data = yaml.safe_load(f)
                return GameConfig(**data)
        return GameConfig()
