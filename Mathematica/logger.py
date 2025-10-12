import os

LOG_FILE = "rewrite_log.txt"
STEP_COUNTER = 0

def log_step(description: str):
    global STEP_COUNTER
    STEP_COUNTER += 1
    with open(LOG_FILE, "a") as f:
        f.write(f"step {STEP_COUNTER}: {description}\n")

def reset_log():
    global STEP_COUNTER
    STEP_COUNTER = 0
    with open(LOG_FILE, "w") as f:
        f.write("")

def total_steps():
    return STEP_COUNTER
