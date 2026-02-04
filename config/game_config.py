import yaml
import os

class GameConfig:
    def __init__(self, **kwargs):
        # Set default values
        defaults = {
            "mode": "human",
            "language": "en",
            "seed": None,
            "character": "Ironclad",
            "debug": True,
            "debug": False,
            "debug_log_path": "logs/debug.log",
        }

        # Update defaults with provided kwargs
        defaults.update(kwargs)

        # Set attributes explicitly for pylint
        self.mode = defaults["mode"]
        self.language = defaults["language"]
        self.seed = defaults["seed"]
        self.character = defaults["character"]
        self.debug = defaults["debug"]
        self.debug_log_path = defaults["debug_log_path"]

    def get(self, key, default=None):
        """Dict-like access for compatibility with config.get usage."""
        return getattr(self, key, default)

    @staticmethod
    def load(config_path):
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                data = yaml.safe_load(f)
                return GameConfig(**data)
        return GameConfig()