import os
from logger import reset_log, get_step_counter, LOG_FILE
from rules import Var, Const, Add, Sub, Mul, Div, Pow, Exp, Log, Sin, Cos, Tan, Neg, Sec, rewrite, Integrate
from differentiation import differentiate
from integration import integrate 
from equality import check_equal
from simplification import simplification_rules
from tests import TESTS

# --- Console Colors ---
RED, GREEN, YELLOW, RESET = "\033[91m", "\033[92m", "\033[93m", "\033[0m"

# Store test results globally for summary reporting
test_results = []
test_failures = []

def print_result(name, passed, expected=None, got=None, test_type=""):
    """
    (MODIFIED) Only records test results and failures to global lists. 
    It DOES NOT print the individual test results to the console, fulfilling the user's request.
    """
    
    # Store result for summary
    test_results.append((name, passed, expected, got, test_type))
    
    # If failed, store details for the final summary
    if not passed:
        test_failures.append({
            "name": name,
            "expected": expected,
            "got": got,
            "type": test_type
        })
    # NOTE: The print statement for individual test results is intentionally removed here.


def run_test(test):
    """Run a single test case."""
    name = test["name"]
    expr = test["expr"]
    expected_expr = test["expected"]
    is_integrate = test.get("integrate_only", False)
    
    reset_log()
    
    if is_integrate:
        result = integrate(expr, "x")
        test_type = "Integration"
    else:
        # Assuming all non-integration tests are differentiation
        result = differentiate(expr, "x")
        test_type = "Differentiation"
    
    # This call now only populates the lists, without printing
    passed = check_equal(result, expected_expr)
    print_result(name, passed, repr(expected_expr), repr(result), test_type)


if __name__ == "__main__":
    # The header remains, but the individual results list is suppressed below this line
    print(f"\nRunning calculus tests...\n{'=' * 60}\n")
    
    # Run all tests (silently)
    for test in TESTS:
        run_test(test)
        
    # --- Final Summary ---
    total_tests = len(TESTS)
    passed_tests = sum(1 for _, passed, _, _, _ in test_results if passed)
    failed_tests = total_tests - passed_tests
    
    print(f"\n{'=' * 60}")
    print(f"{GREEN}SUMMARY:{RESET}")
    print(f"Total tests run: {total_tests}")
    
    # Print the tally lines
    if passed_tests > 0:
        print(f"{GREEN}✅ PASS: {passed_tests}{RESET}")
    if failed_tests > 0:
        print(f"{RED}❌ FAIL: {failed_tests}{RESET}")
    
    if failed_tests > 0:
        print(f"\n{RED}--- DETAILED FAILURES ---{RESET}")
        for i, failure in enumerate(test_failures):
            # Print the detailed failure output
            print(f"\n{i+1}. {failure['type']} Test: {failure['name']}")
            print(f"   Expected: {YELLOW}{failure['expected']}{RESET}")
            print(f"   Got:      {YELLOW}{failure['got']}{RESET}")
    
    print(f"\nTotal rewrite steps logged: {get_step_counter()}")
    print(f"Log written to: {LOG_FILE}")
    print("\nAll tests completed.")