"""Seed input identity through isolated YAML, normal initialization and display."""
import pytest

from config.game_config import GameConfig
from engine.game_flow import GameFlow
import engine.game_flow as flow_module
import engine.game_state as state_module
from utils.seed import encode_seed


@pytest.mark.parametrize("field,code,expected", [
    ("seed_code", "20261029", 128792684204),
    ("seed", "ABC123", 542241423),
    ("seed_code", " abc123 ", 542241423),
    ("seed_code", "O1", 1),
    ("seed_code", "01", 1),
    ("seed_code", "0", 0),
    ("seed_code", encode_seed(-1), -1),
    ("seed_code", encode_seed(-(1 << 63)), -(1 << 63)),
    ("seed_code", encode_seed((1 << 63) - 1), (1 << 63) - 1),
])
def test_code_normal_startup_and_display(tmp_path, monkeypatch, field, code, expected):
    import rooms  # noqa: F401
    import relics  # noqa: F401
    import potions  # noqa: F401
    path = tmp_path / "config.yaml"
    path.write_text(f'{field}: "{code}"\nmode: debug\nlanguage: en\n', encoding="utf-8")
    config = GameConfig.load(path)
    monkeypatch.setattr(GameConfig, "load", staticmethod(lambda _: config))
    monkeypatch.setattr(state_module.time, "time", lambda: 123456789)
    state = state_module.game_state
    state.__init__()
    assert state.config.seed == expected
    assert state.config.seed_specified is True
    assert state.config.seed_code == (encode_seed(expected) or "0")
    flow = GameFlow()
    assert flow._execute_init_act_phase(state) is None
    assert state.map_manager is not None
    output = []
    monkeypatch.setattr(flow_module, "tui_print", output.append)
    flow._display_welcome()
    assert f"Seed: {config.seed_code}" in output


@pytest.mark.parametrize("kwargs", [{}, {"seed": -1}, {"seed_code": ""}, {"seed": "  "}])
def test_automatic_seed_identity_and_resolution(monkeypatch, kwargs):
    config = GameConfig(**kwargs)
    monkeypatch.setattr(GameConfig, "load", staticmethod(lambda _: config))
    monkeypatch.setattr(state_module.time, "time", lambda: 20261029)
    state_module.game_state.__init__()
    assert config.seed == 20261029
    assert config.seed_code == "DHJLJ"
    assert config.seed_specified is False
    config.resolve_seed(42)
    assert config.seed == 20261029


@pytest.mark.parametrize("value", [0, 1, 20261029, -2, -(1 << 63), (1 << 63) - 1])
def test_legacy_integer_semantics(value):
    config = GameConfig(seed=value)
    config.resolve_seed(42)
    assert config.seed == value
    assert config.seed_specified


@pytest.mark.parametrize("kwargs", [
    {"seed_code": "A!"}, {"seed": "-1"}, {"seed_code": "A B"},
    {"seed_code": 123}, {"seed": True}, {"seed": 1.5},
    {"seed": 1 << 63}, {"seed": -(1 << 63) - 1},
    {"seed": 1, "seed_code": "ABC"}, {"seed": "ABC", "seed_code": "ABC"},
])
def test_invalid_seed_rejected_without_fallback(kwargs):
    with pytest.raises(ValueError):
        GameConfig(**kwargs)


def test_zero_seed_code_roundtrip_keeps_explicit_identity():
    config = GameConfig(seed_code="0")
    reloaded = GameConfig(seed_code=config.seed_code)
    assert reloaded.seed == 0 and reloaded.seed_specified
