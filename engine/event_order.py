"""Explicit normal-mode event order from original dungeon initialization methods.

Only ordering lives here. Existing eligibility/category/weight protocols retain
their own audit scope; filtering and used-event removal must preserve this order.
"""

EVENTS = {
    1: ("big_fish", "the_cleric", "dead_adventurer", "golden_idol", "wing_statue",
        "world_of_goop", "the_ssssserpent", "living_wall", "hypnotizing_mushrooms",
        "scrap_ooze", "shining_light"),
    2: ("pleading_vagrant", "ancient_writing", "old_beggar", "the_colosseum",
        "cursed_tome", "augmenter", "forgotten_altar", "council_of_ghosts",
        "masked_bandits", "the_nest", "the_library", "the_mausoleum", "vampires"),
    3: ("falling", "mind_bloom", "the_moai_head", "mysterious_sphere", "sensory_stone",
        "tomb_of_lord_red_mask", "winding_halls"),
}
SHRINES = {
    1: ("match_and_keep", "golden_shrine", "transmogrifier", "purifier", "upgrade_shrine", "wheel_of_change"),
    2: ("match_and_keep", "wheel_of_change", "golden_shrine", "transmogrifier", "purifier", "upgrade_shrine"),
    3: ("match_and_keep", "wheel_of_change", "golden_shrine", "transmogrifier", "purifier", "upgrade_shrine"),
}
SPECIAL = ("ominous_forge", "bonfire_spirits", "designer_in_spire", "duplicator", "face_trader",
           "divine_fountain", "knowing_skull", "lab", "nloth", "a_note_for_yourself",
           "secret_portal", "the_joust", "we_meet_again", "woman_in_blue")


def ordered_ids(act: int, registered) -> list[str]:
    original = EVENTS.get(act, ()) + SHRINES.get(act, ()) + SPECIAL
    known = set(original)
    # Extensions/unrecognized test events remain deterministic and never
    # reorder original entries through registration/import order.
    return [key for key in original if key in registered] + sorted(set(registered) - known)
