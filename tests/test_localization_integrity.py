import re

from localization import translations


PLACEHOLDER_PATTERN = re.compile(r"\{([^{}]+)\}")


def test_all_localization_key_sets_match_between_en_and_zh():
    en_keys = set(translations["en"].keys())
    zh_keys = set(translations["zh"].keys())

    missing_in_zh = sorted(en_keys - zh_keys)
    extra_in_zh = sorted(zh_keys - en_keys)

    assert not missing_in_zh, (
        "Localization keys missing in zh:\n" + "\n".join(missing_in_zh)
    )
    assert not extra_in_zh, (
        "Unexpected localization keys present only in zh:\n" + "\n".join(extra_in_zh)
    )


def test_all_localization_placeholders_match_between_en_and_zh():
    mismatches = []
    shared_keys = sorted(set(translations["en"].keys()) & set(translations["zh"].keys()))

    for key in shared_keys:
        en_placeholders = set(PLACEHOLDER_PATTERN.findall(str(translations["en"][key])))
        zh_placeholders = set(PLACEHOLDER_PATTERN.findall(str(translations["zh"][key])))
        if en_placeholders != zh_placeholders:
            mismatches.append(
                f"{key}: en={sorted(en_placeholders)} zh={sorted(zh_placeholders)}"
            )

    assert not mismatches, (
        "Localization placeholder mismatches between en and zh:\n"
        + "\n".join(mismatches)
    )


def test_no_deprecated_localization_alias_keys_remain():
    deprecated_prefixes = (
        "action.",
        "rooms.RestRoom.RestRoom.",
        "rooms.ShopRoom.ShopRoom.",
        "rooms.TreasureRoom.treasure.",
        "rooms.rest.",
        "rooms.shop.",
        "rooms.treasure.",
        "powers.Thievery.",
        "enemies.SlimeBoss.intentions.goop_pray.",
    )

    deprecated_keys = []
    for lang in ("en", "zh"):
        for key in sorted(translations[lang].keys()):
            if key.startswith(deprecated_prefixes):
                deprecated_keys.append(f"{lang}: {key}")

    assert not deprecated_keys, (
        "Deprecated localization alias keys still present:\n"
        + "\n".join(deprecated_keys)
    )
