import re

from localization import translations
from rooms.event import EventRoom
from rooms.rest import RestRoom
from rooms.shop import ShopRoom
from rooms.treasure import TreasureRoom


PLACEHOLDER_PATTERN = re.compile(r"\{([^{}]+)\}")
CJK_PATTERN = re.compile(r"[\u4e00-\u9fff]")


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


def test_no_placeholder_question_marks_in_known_zh_localizations():
    broken_keys = {
        "cards.colorless.Impatience.description",
        "powers.Constricted.name",
        "powers.Constricted.description",
        "enemies.Nemesis.name",
        "enemies.Nemesis.intentions.Tri Attack.name",
        "enemies.Nemesis.intentions.Tri Attack.description",
        "enemies.Nemesis.intentions.Tri Burn.name",
        "enemies.Nemesis.intentions.Tri Burn.description",
        "enemies.Nemesis.intentions.Scythe.name",
        "enemies.Nemesis.intentions.Scythe.description",
        "enemies.SpikeSlimeL.intentions.lick.description",
    }

    offenders = []
    for key in sorted(broken_keys):
        value = str(translations["zh"][key])
        if "??" in value or "???" in value:
            offenders.append(f"{key}: {value}")

    assert not offenders, (
        "Known zh localization entries still contain placeholder question marks:\n"
        + "\n".join(offenders)
    )


def test_room_local_keys_resolve_through_rooms_prefix():
    assert ShopRoom().local("title").resolve() == "Shop"
    assert RestRoom().local("title").resolve() == "Rest Site"
    assert TreasureRoom().local("title").resolve() == "Treasure Room"
    assert EventRoom().local("enter").resolve() == "You encounter an event."


def test_mind_bloom_description_exists_in_both_languages():
    assert translations["en"]["events.mind_bloom.description"] != "events.mind_bloom.description"
    assert translations["zh"]["events.mind_bloom.description"] != "events.mind_bloom.description"


def test_shiv_localization_lives_under_colorless_namespace():
    for language in ("en", "zh"):
        assert f"cards.colorless.Shiv.name" in translations[language]
        assert f"cards.colorless.Shiv.description" in translations[language]
        assert f"cards.silent.Shiv.name" not in translations[language]
        assert f"cards.silent.Shiv.description" not in translations[language]


def test_en_localization_contains_no_chinese_characters():
    offenders = []
    for key, value in sorted(translations["en"].items()):
        if CJK_PATTERN.search(str(value)):
            offenders.append(f"{key}: {value}")

    assert not offenders, (
        "English localization still contains Chinese text:\n"
        + "\n".join(offenders[:50])
    )


def test_selected_official_chinese_names_match_current_localization():
    expected = {
        "cards.ironclad.Bash.name": "痛击",
        "cards.ironclad.Uppercut.name": "上勾拳",
        "cards.colorless.DramaticEntrance.name": "闪亮登场",
        "powers.Constricted.name": "缠绕",
        "powers.EntangledPower.name": "缠身",
        "powers.FlexPower.name": "活动肌肉",
        "relics.AncientTeaSet.name": "古茶具套装",
        "relics.BirdFacedUrn.name": "鸟面瓮",
        "relics.BottledFlame.name": "瓶装火焰",
        "relics.MercuryHourglass.name": "水银沙漏",
        "enemies.Nemesis.name": "天罚",
        "enemies.Spiker.name": "钉刺机",
        "enemies.SpireShield.name": "高塔之盾",
        "enemies.SpireSpear.name": "高塔之矛",
    }

    mismatches = []
    for key, value in expected.items():
        actual = translations["zh"].get(key)
        if actual != value:
            mismatches.append(f"{key}: expected={value} actual={actual}")

    assert not mismatches, (
        "Selected official Chinese localization entries do not match:\n"
        + "\n".join(mismatches)
    )
