from powers.definitions.fading import FadingPower


def test_fading_power_description_localization_has_default_key():
    power = FadingPower(duration=3)

    description = power.local("description", amount=power.duration).resolve()

    assert description


from powers.definitions.panache import PanachePower


def test_panache_power_name_localization_uses_fallback_alias():
    power = PanachePower(amount=10)

    name = power.local("name").resolve()

    assert name == "Panache"
    assert not name.startswith("powers.")
