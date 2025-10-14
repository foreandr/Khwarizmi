# ============================================================
# logger.py — Hierarchical Step Logger for Symbolic Engine
# ============================================================

import os
import sys

LOG_FILE = "rewrite_log.txt"
STEP_COUNTER = 0
DEPTH = 0


# ---------------- Depth Control ----------------

def push_depth():
    """Increase indentation depth (used for nested recursion)."""
    global DEPTH
    DEPTH += 1


def pop_depth():
    """Decrease indentation depth (used after recursion returns)."""
    global DEPTH
    if DEPTH > 0:
        DEPTH -= 1


def get_depth():
    """Return current recursion depth."""
    return DEPTH


# ---------------- Step Logging ----------------

def log_step(description: str, printout=False):
    """Record a single log step with indentation according to recursion depth."""
    global STEP_COUNTER
    STEP_COUNTER += 1

    indent = "  " * DEPTH
    message = f"[depth {DEPTH}] {description}"

    # Write safely using UTF-8 (handles symbols like ∫, π, etc.)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"step {STEP_COUNTER}: {indent}{message}\n")
    except Exception as e:
        print(f"[Logger Error] Could not write to log: {e}", file=sys.stderr)

    # Print to console — also handle Unicode safely
    if printout:
        try:
            print(f"step {STEP_COUNTER}: {indent}{message}")
        except UnicodeEncodeError:
            safe_msg = message.encode("ascii", "replace").decode()
            print(f"step {STEP_COUNTER}: {indent}{safe_msg}")


def reset_log():
    """Reset the step counter and clear the log file."""
    global STEP_COUNTER, DEPTH

    # --- Stylized reset banner in PURPLE ---
    PURPLE, GREEN, YELLOW, RESET = "\033[95m", "\033[92m", "\033[93m", "\033[0m"
    print(f"{PURPLE}* {YELLOW}LOG AND STEP COUNTER RESET INITIATED{PURPLE} *")
    print(f"{PURPLE}* {GREEN}STARTING A CLEAN TEST RUN NOW!{PURPLE}      *")
    print(f"{PURPLE}=" * 40 + RESET)
    # ---------------------------------------

    STEP_COUNTER = 0
    DEPTH = 0
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("")



def get_step_counter() -> int:
    """Return the total number of logged steps."""
    return STEP_COUNTER
