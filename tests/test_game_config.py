from config.game_config import GameConfig


def test_game_config_load_reads_utf8_bom_mode_key():
    config_path = "tests/_tmp_game_config_bom.yaml"
    try:
        with open(config_path, "w", encoding="utf-8-sig") as handle:
            handle.write("mode: human\nauto_select: false\ncharacter: Silent\n")

        config = GameConfig.load(config_path)

        assert config.mode == "human"
        assert config.auto_select is False
        assert config.character == "Silent"
    finally:
        import os

        if os.path.exists(config_path):
            os.remove(config_path)
