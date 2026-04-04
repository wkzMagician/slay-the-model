"""Watcher character configuration."""
from player.character_config import register_character


@register_character(
    name="watcher",
    display_name="Watcher",
    max_hp=72,
    energy=3,
    gold=99,
    deck=[
        "watcher.strike",
        "watcher.strike",
        "watcher.strike",
        "watcher.strike",
        "watcher.defend",
        "watcher.defend",
        "watcher.defend",
        "watcher.defend",
        "watcher.eruption",
        "watcher.vigilance",
    ],
    starting_relics=["PureWater"],
    orb_slots=1,
    potion_limit=3,
    draw_count=5,
)
class WatcherConfig:
    pass
