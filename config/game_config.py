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

        # Set attributes dynamically
        for key, value in defaults.items():
            setattr(self, key, value)

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