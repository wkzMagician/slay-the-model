import localization

def test_silent_zh_localization_has_real_text():
    localization.set_language('zh')
    assert localization.t('cards.silent.Accuracy.name') == '精准'
    assert '小刀' in localization.t('cards.silent.Accuracy.description')
    localization.set_language('en')
