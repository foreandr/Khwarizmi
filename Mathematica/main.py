import os
from logger import reset_log, get_step_counter, LOG_FILE
from rules import Var, Const, Add, Sub, Mul, Div, Pow, Exp, Log, Sin, Cos, Tan, Neg, Sec, rewrite
from differentiation import differentiate
from equality import check_equal
from simplification import simplification_rules
from tests import TESTS

# --- Console Colors ---
RED, GREEN, YELLOW, RESET = "\033[91m", "\033[92m", "\033[93m", "\033[0m"

def print_result(name, passed, expected=None, got=None):
    """Prints colored test results."""
    status = f"{GREEN}✅ PASS{RESET}" if passed else f"{RED}❌ FAIL{RESET}"
    print(f"{status} - {name}")
    if not passed and expected is not None and got is not None:
        print(f"  Expected: {YELLOW}{expected}{RESET}")
        print(f"  Got:      {YELLOW}{got}{RESET}")
    print("-" * 60)

def run_test(name, expr, expected_expr, simplify_only=False):
    """Run a differentiation or simplification test."""
    reset_log()
    
    if simplify_only:
        result = rewrite(expr, simplification_rules())
    else:
        result = differentiate(expr, "x")
    
    passed = check_equal(result, expected_expr)
    print_result(name, passed, repr(expected_expr), repr(result))

if __name__ == "__main__":
    print(f"\nRunning differentiation tests...\n{'=' * 60}\n")

    for test in TESTS:
        simplify_only = test.get("simplify_only", False)
        run_test(test["name"], test["expr"], test["expected"], simplify_only)

    total_steps = get_step_counter()
    print(f"\nTotal rewrite steps logged: {YELLOW}{total_steps}{RESET}")
    print(f"Log written to: {YELLOW}{os.path.abspath(LOG_FILE)}{RESET}")
    print("\nAll tests completed.\n")