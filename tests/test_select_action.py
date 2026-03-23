import pytest

from actions.display import InputRequestAction
from utils.option import Option


class TestInputRequestAction:
    def test_build_selected_options_keeps_original_index(self):
        options = [
            Option(name="A", actions=[]),
            Option(name="B", actions=[]),
            Option(name="C", actions=[]),
        ]
        action = InputRequestAction(title="test", options=options)

        selected = action._build_selected_options(options, [2, 0])

        assert list(selected.keys()) == [2, 0]
        assert selected[2].name == "C"
        assert selected[0].name == "A"

    def test_show_choose_prints_original_indices(self, capsys):
        options = [
            Option(name="A", actions=[]),
            Option(name="B", actions=[]),
            Option(name="C", actions=[]),
        ]
        action = InputRequestAction(title="test", options=options)
        selected = action._build_selected_options(options, [2, 0])

        action.show_choose(selected)
        out = capsys.readouterr().out

        assert "3. C" in out
        assert "1. A" in out


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
