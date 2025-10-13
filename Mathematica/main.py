import os
import re
from logger import log_step, reset_log, get_step_counter, LOG_FILE
from rules import *

# ============================================================
# Colored Output Helpers
# ============================================================

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def print_result(name, passed, expected=None, got=None):
    if passed:
        print(f"{GREEN}✅ PASS{RESET} - {name}")
    else:
        print(f"{RED}❌ FAIL{RESET} - {name}")
        if expected is not None and got is not None:
            print(f"   Expected: {YELLOW}{expected}{RESET}")
            print(f"   Got:      {YELLOW}{got}{RESET}")
    print("-" * 60)

# ============================================================
# Normalization Helpers
# ============================================================

def normalize(expr_str: str) -> str:
    """
    Normalize expression strings for fair comparison:
    - Remove spaces
    - Simplify redundant parentheses
    - Remove trailing/leading whitespace
    """
    if expr_str is None:
        return ""
    s = expr_str.strip()
    s = s.replace(" ", "")
    # Normalize redundant parentheses like ((x)) -> (x)
    for _ in range(5):
        s = re.sub(r"\(\s*([^\(\)]*)\s*\)", r"(\1)", s)
        s = s.replace("((", "(").replace("))", ")")
    return s

# ============================================================
# Equality Check using rewrite engine
# ============================================================

def check_equal(expr1: Expr, expr2: Expr) -> bool:
    """
    Determine if two expressions are mathematically equivalent
    by repeatedly simplifying both sides using the rules engine.
    """

    def simplify(expr: Expr) -> Expr:
        prev = None
        while prev != repr(expr):
            prev = repr(expr)
            expr = rewrite(expr, simplification_rules())
            expr = evaluate_constants(expr)
        return expr

    e1 = simplify(expr1)
    e2 = simplify(expr2)

    # canonicalize order of Add / Mul
    def canonicalize(expr: Expr) -> Expr:
        if isinstance(expr, Add):
            a, b = expr.left, expr.right
            if repr(a) > repr(b):
                a, b = b, a
            return Add(canonicalize(a), canonicalize(b))
        if isinstance(expr, Mul):
            a, b = expr.left, expr.right
            if repr(a) > repr(b):
                a, b = b, a
            return Mul(canonicalize(a), canonicalize(b))
        if isinstance(expr, Sub):
            return Sub(canonicalize(expr.left), canonicalize(expr.right))
        if isinstance(expr, Div):
            return Div(canonicalize(expr.left), canonicalize(expr.right))
        if isinstance(expr, Pow):
            return Pow(canonicalize(expr.base), canonicalize(expr.exp))
        if isinstance(expr, Exp):
            return Exp(canonicalize(expr.arg))
        if isinstance(expr, Log):
            return Log(canonicalize(expr.arg))
        if isinstance(expr, Sin):
            return Sin(canonicalize(expr.arg))
        if isinstance(expr, Cos):
            return Cos(canonicalize(expr.arg))
        if isinstance(expr, Tan):
            return Tan(canonicalize(expr.arg))
        return expr

    e1 = canonicalize(e1)
    e2 = canonicalize(e2)

    return repr(e1) == repr(e2)

# ============================================================
# Test Utilities
# ============================================================

def run_test(name, expr, expected_expr):
    reset_log()
    d = differentiate(expr, "x")

    passed = check_equal(d, expected_expr)
    print_result(name, passed, repr(expected_expr), repr(d))

# ============================================================
# Define Expressions (Expr trees for expected values)
# ============================================================

x = Var("x")

TESTS = [
    {
        "name": "Polynomial Derivative",
        "expr": Mul(Const(3), Pow(x, Const(2))),
        "expected": Mul(Const(3), Mul(Const(2), x)),  # 3*(2*x)
    },
    {
        "name": "Exponential Derivative",
        "expr": Exp(Mul(Const(2), x)),
        "expected": Mul(Exp(Mul(Const(2), x)), Const(2)),
    },
    {
        "name": "Logarithmic Derivative",
        "expr": Log(x),
        "expected": Div(Const(1), x),
    },
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
                        Div(Const(1), Pow(Cos(x), Const(2)))  # canonical form here
                    )
                )
            )
        ),
    },
]

# ============================================================
# Run Tests
# ============================================================

if __name__ == "__main__":
    print(f"\nRunning differentiation tests...\n{'=' * 60}\n")
    for test in TESTS:
        run_test(test["name"], test["expr"], test["expected"])

    total_steps = get_step_counter()
    print(f"\nTotal rewrite steps logged: {YELLOW}{total_steps}{RESET}")
    print(f"Log written to: {YELLOW}{os.path.abspath(LOG_FILE)}{RESET}")
    print("\nAll tests completed.\n")
