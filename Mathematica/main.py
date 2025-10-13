# ============================================================
# main.py — Differentiation Test Suite for Symbolic Engine
# ============================================================

import os
from logger import log_step, reset_log, get_step_counter, LOG_FILE
from rules import (
    Var, Const, Add, Sub, Mul, Div, Pow,
    Exp, Log, Sin, Cos, Tan, Neg, Sec,
    differentiate, simplification_rules
)
from equality import check_equal  # ✅ ensures structural equivalence

# ============================================================
# Colored Output Helpers
# ============================================================

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def print_result(name, passed, expected=None, got=None):
    """Prints colored test results with optional expected/actual."""
    if passed:
        print(f"{GREEN}✅ PASS{RESET} - {name}")
    else:
        print(f"{RED}❌ FAIL{RESET} - {name}")
        if expected is not None and got is not None:
            print(f"   Expected: {YELLOW}{expected}{RESET}")
            print(f"   Got:      {YELLOW}{got}{RESET}")
    print("-" * 60)


# ============================================================
# Test Utilities
# ============================================================

def run_test(name, expr, expected_expr, simplify_only=False):
    """Run a differentiation or simplification test."""
    reset_log()
    if simplify_only:
        from rules import rewrite
        result = rewrite(expr, simplification_rules())
    else:
        result = differentiate(expr, "x")
    passed = check_equal(result, expected_expr)
    print_result(name, passed, repr(expected_expr), repr(result))


# ============================================================
# Define Expressions (Expr trees for expected values)
# ============================================================

x = Var("x")

TESTS = [
    # --- Polynomial ---
    {
        "name": "Polynomial Derivative",
        "expr": Mul(Const(3), Pow(x, Const(2))),
        "expected": Mul(Const(3), Mul(Const(2), x)),  # 3*(2*x)
    },

    # --- Exponential ---
    {
        "name": "Exponential Derivative",
        "expr": Exp(Mul(Const(2), x)),
        "expected": Mul(Exp(Mul(Const(2), x)), Const(2)),
    },

    # --- Logarithmic ---
    {
        "name": "Logarithmic Derivative",
        "expr": Log(x),
        "expected": Div(Const(1), x),
    },

    # --- Trigonometric ---
    {
        "name": "Trigonometric Derivative (sin)",
        "expr": Sin(x),
        "expected": Cos(x),
    },
    {
        "name": "Trigonometric Derivative (cos)",
        "expr": Cos(x),
        "expected": Mul(Const(-1), Sin(x)),
    },
    {
        "name": "Trigonometric Derivative (tan)",
        "expr": Tan(x),
        "expected": Div(Const(1), Pow(Cos(x), Const(2))),  # canonical cosine form
    },

    # --- Composite Expression ---
    {
        "name": "Full Composite Expression",
        "expr": Add(
            Add(Mul(Const(3), Pow(x, Const(2))), Const(4)),
            Add(
                Exp(Mul(Const(2), x)),
                Add(
                    Log(x),
                    Add(
                        Sin(x),
                        Add(Cos(x), Tan(x))
                    )
                )
            )
        ),
        "expected": Add(
            Add(Mul(Const(3), Mul(Const(2), x)), Const(0)),
            Add(
                Mul(Exp(Mul(Const(2), x)), Const(2)),
                Add(
                    Div(Const(1), x),
                    Add(
                        Add(Cos(x), Mul(Const(-1), Sin(x))),
                        Div(Const(1), Pow(Cos(x), Const(2)))
                    )
                )
            )
        ),
    },

    # --- Negation Simplification (symbolic only) ---
    {
        "name": "Negation Simplification",
        "expr": Neg(Neg(x)),
        "expected": x,
        "simplify_only": True,
    },

    # --- Negation Derivative ---
    {
        "name": "Negation Derivative",
        "expr": Neg(Neg(x)),
        "expected": Const(1),
    },

    # --- Reciprocal Trig Simplification (sec) ---
    {
        "name": "Reciprocal Trig Simplification (sec)",
        "expr": Div(Const(1), Cos(x)),
        "expected": Div(Const(1), Cos(x)),
        "simplify_only": True,
    },

    # --- Reciprocal Trig Derivative (sec) ---
    {
        "name": "Reciprocal Trig Derivative (sec)",
        "expr": Div(Const(1), Cos(x)),
        "expected": Mul(Div(Const(1), Cos(x)), Tan(x)),  # (1/cos(x)) * tan(x)
    },
]


# ============================================================
# Run Tests
# ============================================================

if __name__ == "__main__":
    print(f"\nRunning differentiation tests...\n{'=' * 60}\n")

    for test in TESTS:
        simplify_only = test.get("simplify_only", False)
        run_test(test["name"], test["expr"], test["expected"], simplify_only)

    total_steps = get_step_counter()
    print(f"\nTotal rewrite steps logged: {YELLOW}{total_steps}{RESET}")
    print(f"Log written to: {YELLOW}{os.path.abspath(LOG_FILE)}{RESET}")
    print("\nAll tests completed.\n")
