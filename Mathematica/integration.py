# ============================================================
# integration.py — Hierarchical Integration Engine (FINAL FIX V5)
# ============================================================

from rules import Expr, Var, Const, Add, Sub, Mul, Div, Pow, Exp, Log, Sin, Cos, Neg, Integrate, rewrite, Sinh, Sec # <-- EXPR ADDED HERE
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
    
    # CRITICAL FIX: Ensure DEPTH is used correctly
    if get_depth() > 20: 
        log_step("Recursion depth limit reached (20). Returning integral unsolved.")
        if reset: pop_depth()
        return expr if isinstance(expr, Integrate) else Integrate(expr, v)

    # 1. Try U-Substitution first
    u_sub_result = try_u_substitution(expr, v)
    if u_sub_result is not None:
        log_step(f"Returning from U-Substitution: {u_sub_result}")
        return rewrite(u_sub_result, simplification_rules())

    # 2. Try Integration by Parts second
    # Pass the 'integrate' function itself for recursive calls within IBP
    ibp_result = try_integration_by_parts(expr, v, integrate_fn=integrate) 
    if ibp_result is not None:
        log_step(f"Returning from Integration by Parts: {ibp_result}")
        # The result from IBP contains the sub-integral which will be resolved in step 4
        return rewrite(ibp_result, simplification_rules())

    # 3. Fallback: rule-based rewrite 
    if isinstance(expr, Integrate):
        result = expr
    else:
        result = Integrate(expr, v)
        
    # Apply foundational rules (linearity, basic antiderivatives) until stable
    prev = None
    while prev != repr(result):
        prev = repr(result)
        result = rewrite(result, integration_rules(var))
        result = rewrite(result, simplification_rules())

    # 4. Recursively resolve remaining sub-integrals (e.g., from IBP chains, after linearity)
    def resolve_sub_integrals(expr: Expr) -> Expr:
        if isinstance(expr, Integrate):
            log_step(f"Recursively integrating sub-term: {expr.expr}")
            original_integrand = expr.expr
            
            push_depth() 
            # Re-call integrate on the integrand to solve it
            solved_expr = integrate(original_integrand, var, reset=False)
            pop_depth()
            
            # Optional good practice fix: Simplify the result before comparison
            solved_expr = rewrite(solved_expr, simplification_rules()) 

            if isinstance(solved_expr, Integrate) and check_equal(solved_expr.expr, original_integrand):
                 log_step("Integral is structurally equivalent to its unsolved form. Halting sub-recursion.")
                 return expr
            
            return solved_expr
        
        # NOTE: This relies on Expr objects being dataclasses with __dataclass_fields__
        fields = getattr(expr, "__dataclass_fields__", {})
        new_args = []
        changed = False
        
        for name, field_type in fields.items():
            val = getattr(expr, name)
            if isinstance(val, Expr):
                new_val = resolve_sub_integrals(val)
                if new_val != val:
                    changed = True
                new_args.append(new_val)
            else:
                new_args.append(val)
                
        return type(expr)(*new_args) if changed else expr

    result = resolve_sub_integrals(result)
    result = rewrite(result, simplification_rules()) 
    
    if reset:
        pop_depth()
        
    log_step(f"Final integration result: {result}")
    return result


# ------------------------------------------------------------
# DEBUG HARNESS (Including all 12 tests)
# ------------------------------------------------------------
if __name__ == "__main__":
    print("\n=== Integration Debug Harness (Hierarchical Logger) ===\n")

    x = Var("x")
    # Note: Ensure all test expression symbols (like Sinh, Sec) are imported at the top from rules.

    tests = [
        # ----------------------------------------------------------------------
        # --- ORIGINAL (PASSED) TESTS ---
        # ----------------------------------------------------------------------
        (
            "Combined (x*e^x + cos(x^2)*2x)",
            Add(
                Mul(x, Exp(x)),
                Mul(Cos(Pow(x, Const(2))), Mul(Const(2), x))
            )
        ),
        (
            "U-Sub: Missing constant factor (x*e^(x^2))",
            Mul(x, Exp(Pow(x, Const(2))))
        ),
        (
            "U-Sub: sin(x^2)*2x",
            Mul(Sin(Pow(x, Const(2))), Mul(Const(2), x))
        ),
        (
            "IBP Nested: x^2 * e^x",
            Mul(Pow(x, Const(2)), Exp(x))
        ),
        (
            "Log Rule variant (2x/(x^2+3))",
            Div(Mul(Const(2), x), Add(Pow(x, Const(2)), Const(3)))
        ),
        # ----------------------------------------------------------------------
        # --- NEW BASIC RULES & POWER RULE TESTS ---
        # ----------------------------------------------------------------------
        (
            "Basic: Constant (5)",
            Const(5)
        ),
        (
            "Basic: Power Rule (x^3)",
            Pow(x, Const(3))
        ),
        (
            "Basic: Negative Power (1/x^3)",
            Div(Const(1), Pow(x, Const(3)))
        ),
        (
            "Basic: Fractional Power (1/sqrt(x))",
            Pow(x, Div(Const(-1), Const(2)))
        ),
        (
            "Basic: Simple Trig (cos(x))",
            Cos(x)
        ),
        # ----------------------------------------------------------------------
        # --- NEW INTEGRATION BY PARTS (IBP) TESTS ---
        # ----------------------------------------------------------------------
        (
            "IBP Simple: x*e^x (Standalone)",
            Mul(x, Exp(x))
        ),
        (
            "IBP Log: ln(x)",
            Log(x)
        ),
        (
            "IBP Simple: x*cos(x)",
            Mul(x, Cos(x))
        ),
        # ----------------------------------------------------------------------
        # --- NEW U-SUBSTITUTION TESTS ---
        # ----------------------------------------------------------------------
        (
            "U-Sub: Linear Exponential (e^3x)",
            Exp(Mul(Const(3), x))
        ),
        (
            "U-Sub: Missing Factor Log (x/(x^2+1))",
            Div(x, Add(Pow(x, Const(2)), Const(1)))
        ),
        (
            "U-Sub: Trig Power (cos^3(x)*sin(x))",
            Mul(Pow(Cos(x), Const(3)), Sin(x))
        ),
        (
            "U-Sub: Complex Fractional Power",
            Pow(Add(x, Const(1)), Div(Const(-1), Const(2)))
        ),
        (
            "U-Sub: Nested Log Power (ln(x)/x)",
            Div(Log(x), x)
        ),
        # ----------------------------------------------------------------------
        # --- NEW SPECIAL FUNCTION TESTS ---
        # ----------------------------------------------------------------------
        (
            "Special: Inverse Trig (1/(1+x^2))",
            Div(Const(1), Add(Const(1), Pow(x, Const(2))))
        ),
        (
            "Basic: Hyperbolic (sinh(x))",
            Sinh(x) 
        ),
        (
            "U-Sub: Trig Identity (sec^2(2x))",
            Pow(Sec(Mul(Const(2), x)), Const(2)) 
        ),
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