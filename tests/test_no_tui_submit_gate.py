import subprocess
import sys


def test_no_tui_mode_succeeds_ten_times():
    for _ in range(10):
        completed = subprocess.run(
            [sys.executable, "__main__.py", "--no-tui"],
            check=False,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        assert completed.returncode == 0
