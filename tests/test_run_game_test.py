import builtins
import queue
from io import BytesIO
from pathlib import Path
from unittest.mock import Mock, mock_open

import tests.run_game_test as runner


def test_run_game_targets_repo_root_main(monkeypatch):
    captured = {}

    dummy_process = Mock()
    dummy_process.stdout = BytesIO()
    dummy_process.stderr = BytesIO()
    dummy_process.returncode = 0
    dummy_process.poll.return_value = 0
    dummy_process.terminate.return_value = None
    dummy_process.wait.return_value = None

    def fake_popen(*args, **kwargs):
        captured["args"] = args
        captured["kwargs"] = kwargs
        return dummy_process

    def fake_get(timeout=0.1):
        raise queue.Empty

    monkeypatch.setattr(runner.subprocess, "Popen", fake_popen)
    monkeypatch.setattr(runner.threading.Thread, "start", lambda self: None)
    monkeypatch.setattr(runner.threading.Thread, "join", lambda self, timeout=None: None)
    monkeypatch.setattr(runner.OUTPUT_QUEUE, "get", fake_get)
    monkeypatch.setattr(builtins, "open", mock_open())
    monkeypatch.setattr(runner.os, "makedirs", lambda *args, **kwargs: None)

    return_code, output_lines, error_lines, game_ended = runner.run_game(timeout=1)

    assert Path(captured["args"][0][1]).name == "__main__.py"
    assert return_code == 0
    assert output_lines == []
    assert error_lines == []
    assert game_ended is False
