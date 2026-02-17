import yaml
import os

class GameConfig:
    def __init__(self, **kwargs):
        # Set default values matching game_config.yaml structure
        defaults = {
            "mode": "human",
            "language": "en",
            "seed": -1,
            "character": "Ironclad",
            "select_overflow": "truncate",
            "human": {
                "auto_select": False,
                "show_menu_option": True,
            },
            "ai": {
                # todo: AI-specific settings will be added here
            },
            "debug": {
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
        self.seed = defaults["seed"]
        self.character = defaults["character"]
        self.select_overflow = defaults["select_overflow"]
        self.human = defaults["human"]
        self.ai = defaults["ai"]
        self.debug = defaults["debug"]

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
            with open(config_path, "r") as f:
                data = yaml.safe_load(f)
                return GameConfig(**data)
        return GameConfig()