import os
from logger import reset_log, get_step_counter, LOG_FILE
from rules import Var, Const, Add, Sub, Mul, Div, Pow, Exp, Log, Sin, Cos, Tan, Neg, Sec, rewrite, Integrate
from differentiation import differentiate
from integration import integrate # NEW: Import integrate
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

def run_test(name, expr, expected_expr, simplify_only=False, integrate_only=False):
    """Run a differentiation, simplification, or integration test."""
    reset_log()
    
    if simplify_only:
        result = rewrite(expr, simplification_rules())
        # test_type = "Simplification"
    elif integrate_only: # CORRECT LOGIC
        result = integrate(expr, "x")
        # test_type = "Integration"
    else:
        result = differentiate(expr, "x")
        # test_type = "Differentiation"
    
    passed = check_equal(result, expected_expr)
    print_result(name, passed, repr(expected_expr), repr(result))

if __name__ == "__main__":
    print(f"\nRunning calculus tests...\n{'=' * 60}\n")

    for test in TESTS:
        simplify_only = test.get("simplify_only", False)
        integrate_only = test.get("integrate_only", False)
        
        run_test(
            test["name"], 
            test["expr"], 
            test["expected"], 
            simplify_only=simplify_only, 
            integrate_only=integrate_only
        )

    print(f"\nTotal rewrite steps logged: {get_step_counter()}")
    print(f"Log written to: {LOG_FILE}\n")
    print("All tests completed.")