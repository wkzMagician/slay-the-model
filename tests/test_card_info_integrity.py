import importlib

from utils.registry import get_registered, list_registered


def test_registered_card_info_renders_without_missing_magic_fields():
    importlib.import_module("cards.colorless")
    importlib.import_module("cards.ironclad")
    importlib.import_module("cards.silent")
    importlib.import_module("cards.defect")

    failures = []
    for card_name in list_registered("card"):
        card_cls = get_registered("card", card_name)
        if card_cls is None:
            continue

        try:
            info = str(card_cls().info())
        except Exception as exc:
            failures.append(f"{card_name}: {exc}")
            continue

        assert info

    assert failures == []


def test_known_card_info_renders_for_magic_placeholder_cards():
    from cards.colorless.ritual_dagger import RitualDagger
    from cards.ironclad.feed import Feed
    from cards.ironclad.rampage import Rampage

    assert str(RitualDagger().info())
    assert str(Feed().info())
    assert str(Rampage().info())
