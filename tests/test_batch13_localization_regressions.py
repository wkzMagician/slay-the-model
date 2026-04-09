import localization


def test_batch13_missing_ui_and_blessing_keys_exist_in_both_languages():
    required_keys = [
        "ui.choose_relic",
        "ui.skip_relic",
        "ui.choose_boss_relic",
        "ui.done",
        "blessing.remove_card_option",
        "blessing.transform_card_option",
        "blessing.replace_starter_relic_option",
        "stance.calm",
        "stance.wrath",
        "stance.choose_stance",
    ]

    for language in ("en", "zh"):
        for key in required_keys:
            assert key in localization.translations[language]


def test_ambrosia_and_duplication_potion_text_matches_current_behavior():
    assert localization.translations["en"]["potions.Ambrosia.description"] == "Enter Divinity."
    assert localization.translations["en"]["potions.DuplicationPotion.description"] == (
        "This turn, your next card is played twice."
    )
    assert localization.translations["zh"]["potions.Ambrosia.description"] == "进入神格。"
    assert localization.translations["zh"]["potions.DuplicationPotion.description"] == (
        "本回合中，你打出的下一张牌会额外触发一次。"
    )


def test_shop_removed_card_message_is_localized_in_chinese():
    original_language = localization.current_language
    try:
        localization.set_language("zh")
        assert localization.t("ui.shop_removed_card", card="打击", price=75) == (
            "已从牌组中移除 打击，花费 75 金币"
        )
    finally:
        localization.set_language(original_language)
