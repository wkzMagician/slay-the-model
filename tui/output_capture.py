# -*- coding: utf-8 -*-
"""
Output capture system - hooks stdout to route print() to TUI panels.
"""
import sys
from typing import Optional, Callable, TextIO
from io import StringIO


class OutputCapture:
    """Captures stdout and routes to TUI callback while preserving original output."""
    
    def __init__(self, callback: Callable[[str], None], original_stdout: Optional[TextIO] = None):
        self.callback = callback
        self.original_stdout = original_stdout or sys.stdout
        self._buffer = StringIO()
        self._enabled = True
    
    def write(self, text: str):
        """Write to both TUI callback and original stdout."""
        if not self._enabled:
            self.original_stdout.write(text)
            return
        
        # Capture for callback
        if text and text.strip():
            self.callback(text)
        
        # Also write to original stdout for debugging
        self.original_stdout.write(text)
    
    def flush(self):
        """Flush both streams."""
        self.original_stdout.flush()
    
    def enable(self):
        """Enable TUI capture."""
        self._enabled = True
    
    def disable(self):
        """Disable TUI capture (use original stdout only)."""
        self._enabled = False
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        return False


class TeeStream:
    """Duplicate writes to multiple streams."""
    
    def __init__(self, *streams):
        self.streams = list(streams)
    
    def write(self, data):
        for stream in self.streams:
            stream.write(data)
            stream.flush()
    
    def flush(self):
        for stream in self.streams:
            stream.flush()
    
    def add_stream(self, stream):
        """Add a stream to tee to."""
        self.streams.append(stream)
    
    def remove_stream(self, stream):
        """Remove a stream from tee."""
        if stream in self.streams:
            self.streams.remove(stream)


def install_output_capture(callback: Callable[[str], None]) -> OutputCapture:
    """
    Install output capture on sys.stdout.
    Returns the OutputCapture instance for later cleanup.
    """
    capture = OutputCapture(callback, sys.stdout)
    sys.stdout = capture
    return capture


def uninstall_output_capture(capture: OutputCapture):
    """Restore original stdout."""
    sys.stdout = capture.original_stdout
