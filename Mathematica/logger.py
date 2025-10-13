# logger.py

LOG_FILE = "rewrite_log.txt"
STEP_COUNTER = 0

def log_step(description: str):
    """
    Appends a step description to the log file and increments the step counter.
    """
    global STEP_COUNTER
    STEP_COUNTER += 1
    with open(LOG_FILE, "a") as f:
        f.write(f"step {STEP_COUNTER}: {description}\n")

def reset_log():
    """
    Resets the step counter and clears the log file.
    """
    global STEP_COUNTER
    STEP_COUNTER = 0
    # Clears the file content
    with open(LOG_FILE, "w") as f:
        f.write("")

def get_step_counter() -> int:
    """
    Returns the current value of the step counter.
    """
    return STEP_COUNTER