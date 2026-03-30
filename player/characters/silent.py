"""Silent character configuration."""
from player.character_config import register_character


@register_character(
    name="silent",
    display_name="Silent",
    max_hp=70,
    energy=3,
    gold=99,
    deck=[
        "silent.strike",
        "silent.strike",
        "silent.strike",
        "silent.strike",
        "silent.strike",
        "silent.defend",
        "silent.defend",
        "silent.defend",
        "silent.defend",
        "silent.defend",
        "silent.neutralize",
        "silent.survivor",
    ],
    starting_relics=["RingOfTheSnake"],
    orb_slots=1,
    potion_limit=3,
    draw_count=5,
)
class SilentConfig:
    """Silent character configuration."""

    pass
