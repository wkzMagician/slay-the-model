import importlib
import inspect

from localization import set_language, t


DEFECT_POWER_MODULES = [
    "amplify",
    "biased_cognition",
    "buffer",
    "creative_ai",
    "echo_form",
    "electro",
    "focus",
    "heatsinks",
    "hello_world",
    "lock_on",
    "loop",
    "machine_learning",
    "self_repair",
    "static_discharge",
    "storm",
]


def _collect_defect_card_names() -> list[str]:
    module = importlib.import_module("cards.defect")
    return sorted(
        obj.__name__
        for obj in vars(module).values()
        if inspect.isclass(obj) and getattr(obj, "__module__", "").startswith("cards.defect.")
    )


def _collect_defect_relic_names() -> list[str]:
    module = importlib.import_module("relics.character.defect")
    return sorted(
        obj.__name__
        for obj in vars(module).values()
        if inspect.isclass(obj) and getattr(obj, "__module__", "") == "relics.character.defect"
    )


def _collect_defect_power_names() -> list[str]:
    names: set[str] = set()
    for module_name in DEFECT_POWER_MODULES:
        module = importlib.import_module(f"powers.definitions.{module_name}")
        for obj in vars(module).values():
            if inspect.isclass(obj) and getattr(obj, "__module__", "") == module.__name__ and obj.__name__.endswith("Power"):
                names.add(obj.__name__)
    return sorted(names)


def test_defect_localization_has_real_text_for_en_and_zh():
    original_language = "en"
    missing: list[str] = []
    try:
        for language in ("en", "zh"):
            set_language(language)

            for card_name in _collect_defect_card_names():
                for suffix in ("name", "description"):
                    key = f"cards.defect.{card_name}.{suffix}"
                    value = t(key)
                    if value == key:
                        missing.append(f"{language}:{key}")

            for relic_name in _collect_defect_relic_names():
                for suffix in ("name", "description"):
                    key = f"relics.{relic_name}.{suffix}"
                    value = t(key)
                    if value == key:
                        missing.append(f"{language}:{key}")

            for power_name in _collect_defect_power_names():
                for suffix in ("name", "description"):
                    key = f"powers.{power_name}.{suffix}"
                    value = t(key)
                    if value == key:
                        missing.append(f"{language}:{key}")
    finally:
        set_language(original_language)

    assert not missing, "Missing Defect localization entries:\n" + "\n".join(missing)
