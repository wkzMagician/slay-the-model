#!/usr/bin/env python
"""
Game System Test Runner
Runs the game as a subprocess and captures output for analysis.
"""
import subprocess
import sys
import os
import threading
import queue
import time
from datetime import datetime

OUTPUT_QUEUE = queue.Queue()
ERROR_DETECTED = False
ERROR_DETAILS = []

def read_stream(stream, stream_name):
    """Read from a stream and put lines in queue."""
    try:
        for line in iter(stream.readline, ''):
            if line:
                OUTPUT_QUEUE.put((stream_name, line.decode('utf-8', errors='replace')))
    finally:
        stream.close()

def run_game(timeout=300):
    """
    Run the game as a subprocess and capture output.
    
    Args:
        timeout: Maximum time to run the game (seconds)
    
    Returns:
        tuple: (return_code, output_lines, error_lines)
    """
    global ERROR_DETECTED, ERROR_DETAILS
    ERROR_DETECTED = False
    ERROR_DETAILS = []
    
    # Create logs directory
    os.makedirs("logs", exist_ok=True)
    
    # Generate log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"logs/game_test_{timestamp}.log"
    
    print(f"Starting game test at {timestamp}")
    print(f"Log file: {log_file}")
    print("-" * 60)
    
    # Start the game process
    process = subprocess.Popen(
        [sys.executable, "__main__.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=os.path.dirname(os.path.abspath(__file__)),
        bufsize=1,  # Line buffered
    )
    
    # Start reader threads
    stdout_thread = threading.Thread(target=read_stream, args=(process.stdout, "STDOUT"))
    stderr_thread = threading.Thread(target=read_stream, args=(process.stderr, "STDERR"))
    stdout_thread.daemon = True
    stderr_thread.daemon = True
    stdout_thread.start()
    stderr_thread.start()
    
    output_lines = []
    error_lines = []
    last_output_time = time.time()
    game_ended = False
    
    with open(log_file, 'w', encoding='utf-8') as log:
        log.write(f"Game Test Log - Started at {timestamp}\n")
        log.write("=" * 60 + "\n\n")
        
        start_time = time.time()
        
        while True:
            try:
                stream_name, line = OUTPUT_QUEUE.get(timeout=0.1)
                last_output_time = time.time()
                
                # Store the line
                if stream_name == "STDERR":
                    error_lines.append(line)
                    # Check for error patterns
                    if "Error" in line or "Exception" in line or "Traceback" in line:
                        ERROR_DETECTED = True
                        ERROR_DETAILS.append(line)
                else:
                    output_lines.append(line)
                
                # Print to console
                prefix = "!" if stream_name == "STDERR" else ">"
                print(f"{prefix} {line.rstrip()}")
                
                # Write to log
                log.write(f"[{stream_name}] {line}")
                log.flush()
                
                # Check for game end conditions
                if "Game Over" in line or "Game Over!" in line:
                    print("\n" + "=" * 60)
                    print("GAME OVER detected - Player died")
                    game_ended = True
                elif "congratulations" in line.lower() or "conquered the Spire" in line:
                    print("\n" + "=" * 60)
                    print("VICTORY detected - Player won!")
                    game_ended = True
                elif "Goodbye" in line or "game_exit" in line:
                    print("\n" + "=" * 60)
                    print("Game exit detected")
                    game_ended = True
                    
            except queue.Empty:
                # Check if process has ended
                if process.poll() is not None:
                    print(f"\nProcess ended with return code: {process.returncode}")
                    break
                
                # Check for timeout
                elapsed = time.time() - start_time
                if elapsed > timeout:
                    print(f"\nTimeout ({timeout}s) reached, terminating process...")
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                    break
                
                # Check for no output timeout (30 seconds without output)
                if time.time() - last_output_time > 30:
                    print("\nNo output for 30 seconds, game might be stuck or waiting for input")
                    # Give it more time in case it's processing
                
    # Wait for reader threads to finish
    stdout_thread.join(timeout=2)
    stderr_thread.join(timeout=2)
    
    # Write summary to log
    with open(log_file, 'a', encoding='utf-8') as log:
        log.write("\n" + "=" * 60 + "\n")
        log.write("SUMMARY\n")
        log.write("=" * 60 + "\n")
        log.write(f"Return code: {process.returncode}\n")
        log.write(f"Total output lines: {len(output_lines)}\n")
        log.write(f"Total error lines: {len(error_lines)}\n")
        log.write(f"Game ended normally: {game_ended}\n")
        if ERROR_DETECTED:
            log.write("\nERRORS DETECTED:\n")
            for err in ERROR_DETAILS:
                log.write(err)
    
    return process.returncode, output_lines, error_lines, game_ended

def analyze_output(output_lines, error_lines):
    """Analyze the output and return a summary."""
    summary = {
        "has_errors": len(error_lines) > 0,
        "error_count": len(error_lines),
        "output_count": len(output_lines),
        "errors": [],
        "tracebacks": [],
    }
    
    # Collect errors
    current_traceback = []
    in_traceback = False
    
    for line in error_lines:
        if "Traceback" in line:
            in_traceback = True
            current_traceback = [line]
        elif in_traceback:
            current_traceback.append(line)
            if line.strip() and not line.startswith(" ") and not line.startswith("\t"):
                summary["tracebacks"].append("".join(current_traceback))
                current_traceback = []
                in_traceback = False
    
    if current_traceback:
        summary["tracebacks"].append("".join(current_traceback))
    
    return summary

if __name__ == "__main__":
    return_code, output_lines, error_lines, game_ended = run_game(timeout=300)
    
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    
    summary = analyze_output(output_lines, error_lines)
    
    print(f"Return code: {return_code}")
    print(f"Game ended: {game_ended}")
    print(f"Output lines: {summary['output_count']}")
    print(f"Error lines: {summary['error_count']}")
    print(f"Tracebacks found: {len(summary['tracebacks'])}")
    
    if ERROR_DETECTED or summary['has_errors']:
        print("\n" + "-" * 60)
        print("ERRORS DETECTED!")
        print("-" * 60)
        for tb in summary['tracebacks']:
            print(tb)
            print("-" * 40)
    
    # Exit with error code if errors detected
    if ERROR_DETECTED or summary['has_errors'] or return_code != 0:
        sys.exit(1)
    else:
        print("\nTest completed successfully!")
        sys.exit(0)
