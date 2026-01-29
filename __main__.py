from engine.game_flow import GameFlow
from engine.game_state import game_state
import os
import sys


class TeeStream:
    """Duplicate writes to multiple streams."""
    def __init__(self, *streams):
        self.streams = streams

    def write(self, data):
        for stream in self.streams:
            stream.write(data)
            stream.flush()

    def flush(self):
        for stream in self.streams:
            stream.flush()


def _setup_ai_debug_logging():
    if not game_state.config.get("ai_debug", False):
        return None

    log_path = game_state.config.get("ai_debug_log_path", "logs/ai_debug.log")
    log_dir = os.path.dirname(log_path)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
    log_file = open(log_path, "a", encoding="utf-8")

    sys.stdout = TeeStream(sys.stdout, log_file)
    sys.stderr = TeeStream(sys.stderr, log_file)
    return log_file

if __name__ == "__main__":
    log_file = _setup_ai_debug_logging()
    try:
        game = GameFlow()
        game.start_game()
    except KeyboardInterrupt:
        from localization import t
        print(f"\n{t('ui.game_interrupted', default='Game interrupted by user.')}")
    except Exception as e:
        from localization import t
        print(f"\n{t('ui.game_error', default=f'Game error: {e}', error=e)}")
        import traceback
        traceback.print_exc()
    finally:
        if log_file:
            log_file.close()