# ============================================================
# integration.py — Hierarchical Integration Engine (FIXED)
# ============================================================

from rules import Expr, Var, Const, Add, Sub, Mul, Div, Pow, Exp, Log, Sin, Cos, Neg, Integrate, rewrite, Sinh, Sec 
from simplification import simplification_rules, evaluate_constants
from equality import check_equal
from logger import log_step, reset_log, get_step_counter, LOG_FILE, push_depth, pop_depth, get_depth 
from typing import Optional

# New imports from modularized files
from integration_rules import integration_rules
from integration_strategies import try_u_substitution, try_integration_by_parts 

# ------------------------------------------------------------
# Main Integration Driver
# ------------------------------------------------------------
def integrate(expr: Expr, var: str, reset: bool = True) -> Expr:
    v = Var(var)
    log_step(f"Integrating expression: {expr}")

    if reset:
        push_depth()
    
    if get_depth() > 20: 
        log_step("Recursion depth limit reached (20). Returning integral unsolved.")
        if reset: pop_depth()
        return expr if isinstance(expr, Integrate) else Integrate(expr, v) 

    # 1. Simplify the expression algebraically (needed for 1/x^3 -> x^-3)
    prev_expr_repr = None
    while prev_expr_repr != repr(expr):
        prev_expr_repr = repr(expr)
        expr = rewrite(expr, simplification_rules())
        expr = evaluate_constants(expr)
        
    # 2. Apply elementary/direct rules (Power Rule, Log Rule, Linearity, etc.)
    integral_expr = Integrate(expr, v)
    
    # CRITICAL FIX: Robustly apply direct rules and simplify until stable.
    prev_integral_repr = None
    while True:
        prev_integral_repr = repr(integral_expr)
        
        # Apply integration rules (Power Rule, Linearity, etc.)
        integral_expr = rewrite(integral_expr, integration_rules(var))
        
        # If the direct rule application yielded a result (i.e., not an Integrate), return it.
        if not isinstance(integral_expr, Integrate):
            # CRITICAL: Simplify the result (e.g., calculates -3+1=-2)
            result = evaluate_constants(integral_expr)
            result = rewrite(result, simplification_rules())
            log_step(f"[Direct Rule Success] Antiderivative found: {result}")
            if reset: pop_depth()
            return result # Return the fully simplified result

        # Simplify the integrand/arguments of the new integral.
        new_expr = rewrite(integral_expr.expr, simplification_rules())
        new_expr = evaluate_constants(new_expr)
        integral_expr = Integrate(new_expr, v)
        
        # If applying rules AND simplifying the integrand didn't change the expression, break.
        if prev_integral_repr == repr(integral_expr):
            break
    
    # 3. Apply Strategies on the fully simplified integrand, if direct rules failed.
    current_expr = integral_expr.expr 

    # 3a. Try U-Substitution
    u_sub_result = try_u_substitution(current_expr, v)
    if u_sub_result is not None and not isinstance(u_sub_result, Integrate):
        result = evaluate_constants(u_sub_result)
        result = rewrite(result, simplification_rules())
        log_step(f"U-Substitution successful: {result}")
        if reset: pop_depth()
        return result
    
    # 3b. Try Integration by Parts
    ibp_result = try_integration_by_parts(current_expr, v, integrate_fn=integrate)
    if ibp_result is not None and not isinstance(ibp_result, Integrate):
        result = evaluate_constants(ibp_result)
        result = rewrite(result, simplification_rules())
        log_step(f"Integration by Parts successful: {result}")
        if reset: pop_depth()
        return result

    # 4. Fallback: If no strategy or rule worked, return the final unsolved integral.
    log_step(f"All strategies and direct rules failed. Returning unsolved integral.")
    if reset: pop_depth()
    
    return integral_expr


if __name__ == "__main__":

    print("\n=== Integration Debug Harness (Hierarchical Logger) ===\n")



    x = Var("x")

    # Note: Ensure all test expression symbols (like Sinh, Sec) are imported at the top from rules.



    tests = [
        # ----------------------------------------------------------------------
        # --- POLYNOMIAL CASES (Fixed and Confirmed) ---
        # ----------------------------------------------------------------------
        (
            "Basic: Negative Power (1/x^3)",
            Div(Const(1), Pow(x, Const(3))) # Expected: Div(Pow(x, Const(-2)), Const(-2))
        ),
        (
            "Basic: Log Rule (1/x)",
            Div(Const(1), x) # Expected: Log(Abs(x))
        ),
        # ----------------------------------------------------------------------
        # --- NEXT CRITICAL TEST (U-SUB Strategy Check) ---
        # ----------------------------------------------------------------------
        (
            "Trig: Linear U-Sub (cos(2x))",
            Cos(Mul(Const(2), x)) # Expected: Div(Sin(Mul(Const(2), x)), Const(2))
        )
    ]



    for name, expr in tests:

        reset_log()

        print(f"▶ {name}")

        print(f"Input : {expr}")

        result = integrate(expr, "x", reset=True) 

        print(f"Output: {result}")

        print(f"Total rewrite steps logged: {get_step_counter()}")

        print(f"Log written to: {LOG_FILE}")

        print("-" * 60)