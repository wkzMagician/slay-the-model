"""Ironclad character configuration."""
from player.character_config import register_character


@register_character(
    name="ironclad",
    display_name="Ironclad",
    max_hp=80,
    energy=3,
    gold=99,
    deck=[
        "ironclad.strike",
        "ironclad.strike",
        "ironclad.strike",
        "ironclad.strike",
        "ironclad.strike",
        "ironclad.defend",
        "ironclad.defend",
        "ironclad.defend",
        "ironclad.defend",
        "ironclad.bash",
    ],
    starting_relics=[
        "BurningBlood",
    ],
    orb_slots=1,
    potion_limit=3,
    draw_count=5,
)
class IroncladConfig:
    """Ironclad character configuration.

    Ironclad: A warrior who excels in combat through strength and heavy blows.
    Starting relic: Burning Blood (heal 6 HP after each combat)
    Starting deck: 5 Strike, 4 Defend, 1 Bash
    """
    pass