"""Silent character configuration (example for extensibility)."""
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
        "silent.survivor",
    ],
    starting_relics=[
        "CeramicFish",  # Temporary placeholder - Silent starting relic
    ],
    orb_slots=1,
    potion_limit=3,
    draw_count=5,
)
class SilentConfig:
    """Silent character configuration.

    Silent: A huntress who excels in poison, shivs, and precision.
    Starting relic: Ring of the Snake (gain 1 dexterity)
    Starting deck: 5 Strike, 4 Defend, 1 Survivor
    """
    pass