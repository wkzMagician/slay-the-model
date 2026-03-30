import importlib.util
from pathlib import Path


def _load_main_module():
    repo_root = Path(__file__).resolve().parent.parent
    main_path = repo_root / "__main__.py"
    spec = importlib.util.spec_from_file_location("slay_the_model_main", main_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_main_module_does_not_own_character_card_imports():
    module = _load_main_module()

    assert not hasattr(module, "_import_character_cards")
