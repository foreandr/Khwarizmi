# ============================================================
# integration.py — Hierarchical Integration Engine (FIXED)
# ============================================================

from rules import *
from simplification import *
from differentiation import differentiate
from equality import check_equal
from logger import log_step, reset_log, get_step_counter, LOG_FILE, push_depth, pop_depth, get_depth # Added get_depth
from typing import Optional


# ------------------------------------------------------------
# Integration Rules
# ------------------------------------------------------------
def integration_rules(var: str) -> list[tuple[Expr, Expr]]:
    """Foundational integration rules for linearity and elementary antiderivatives."""
    v = Var(var)
    return [
        # --- Linearity ---
        (Integrate(Add(PatternVar("u"), PatternVar("w")), v),
         Add(Integrate(PatternVar("u"), v), Integrate(PatternVar("w"), v))),

        (Integrate(Mul(Const(PatternVar("c")), PatternVar("u")), v),
         Mul(Const(PatternVar("c")), Integrate(PatternVar("u"), v))),

        # --- Constants ---
        (Integrate(Const(0), v), Const(0)),
        (Integrate(Const(PatternVar("c")), v), Mul(Const(PatternVar("c")), v)),

        # --- Power Rule ---
        (Integrate(Pow(v, Const(PatternVar("n"))), v),
         Div(Pow(v, Add(Const(PatternVar("n")), Const(1))),
             Add(Const(PatternVar("n")), Const(1)))),

        # --- Exponential & Trig ---
        (Integrate(Exp(v), v), Exp(v)),
        (Integrate(Cos(v), v), Sin(v)),
        (Integrate(Sin(v), v), Neg(Cos(v))),

        # --- Hyperbolic-type substitution rule ---
        (Integrate(Div(Var(var),
                       Pow(Add(Pow(Var(var), Const(2)), Const(PatternVar("a2"))),
                           Div(Const(1), Const(2)))),
                   Var(var)),
         Pow(Add(Pow(Var(var), Const(2)), Const(PatternVar("a2"))),
             Div(Const(1), Const(2)))),
    ]


# ------------------------------------------------------------
# U-Substitution
# ------------------------------------------------------------

def robust_constant_ratio(numerator: Expr, denominator: Expr, var: Var) -> Optional[Const]:
    """Calculates the ratio k = numerator / denominator and returns it as a Const if k is a constant."""
    # 1. Try general rewrite/simplification
    ratio = Div(numerator, denominator)
    k_const = rewrite(ratio, simplification_rules())
    if isinstance(k_const, Const):
        return k_const

    # 2. Robust check for variable cancellation (e.g., x / (c * x) -> 1/c)
    if isinstance(numerator, Var) and numerator.name == var.name:
        if isinstance(denominator, Mul) and isinstance(denominator.right, Var) and denominator.right.name == var.name and isinstance(denominator.left, Const):
            # Form is x / (c * x)
            return Div(Const(1), denominator.left)
        
    return None

def try_u_substitution(integrand: Expr, var: Var) -> Optional[Expr]:
    v = var
    log_step(f"Attempting U-Substitution on {integrand}")

    # --- Logarithmic case: ∫ u'/u dx = ln|u| ---
    if isinstance(integrand, Div):
        u = integrand.right
        u_prime = differentiate(u, v.name)
        if check_equal(integrand.left, u_prime):
            log_step(f"U-Sub success (log rule): u = {u}")
            return Log(u)

        # proportional u'-multiplier check
        k_const = robust_constant_ratio(integrand.left, u_prime, v)
        if isinstance(k_const, Const):
            k = k_const.value
            log_step(f"Proportional U-Sub detected (log rule): scaled by {k}")
            return Mul(Const(k), Log(u))

    # --- f(u)*u' case ---
    if isinstance(integrand, Mul):
        for f_u_candidate, du_candidate in [(integrand.left, integrand.right),
                                            (integrand.right, integrand.left)]:

            # Power Rule
            if isinstance(f_u_candidate, Pow) and isinstance(f_u_candidate.exp, Const):
                if f_u_candidate.exp.value == -1:
                    continue
                u = f_u_candidate.base
                n = f_u_candidate.exp
                u_prime = differentiate(u, v.name)
                
                if check_equal(du_candidate, u_prime):
                    log_step(f"U-Sub success (power rule): u = {u}")
                    return Div(Pow(u, Add(n, Const(1))), Add(n, Const(1)))

                # proportional u' check
                k_const = robust_constant_ratio(du_candidate, u_prime, v)
                if isinstance(k_const, Const):
                    k = k_const.value
                    log_step(f"Proportional U-Sub detected (power rule): scaled by {k}")
                    return Mul(Const(k),
                                Div(Pow(u, Add(n, Const(1))), Add(n, Const(1))))

            # Cosine
            if isinstance(f_u_candidate, Cos):
                u = f_u_candidate.arg
                u_prime = differentiate(u, v.name)
                if check_equal(du_candidate, u_prime):
                    log_step(f"U-Sub success (cos rule): u = {u}")
                    return Sin(u)

                # proportional check
                k_const = robust_constant_ratio(du_candidate, u_prime, v)
                if isinstance(k_const, Const):
                    k = k_const.value
                    log_step(f"Proportional U-Sub detected (cos rule): scaled by {k}")
                    return Mul(Const(k), Sin(u))

            # Sine
            if isinstance(f_u_candidate, Sin):
                u = f_u_candidate.arg
                u_prime = differentiate(u, v.name)
                if check_equal(du_candidate, u_prime):
                    log_step(f"U-Sub success (sin rule): u = {u}")
                    return Neg(Cos(u))

                # proportional check
                k_const = robust_constant_ratio(du_candidate, u_prime, v)
                if isinstance(k_const, Const):
                    k = k_const.value
                    log_step(f"Proportional U-Sub detected (sin rule): scaled by {k}")
                    return Mul(Const(k), Neg(Cos(u)))

            # Exponential
            if isinstance(f_u_candidate, Exp):
                u = f_u_candidate.arg
                u_prime = differentiate(u, v.name)
                if check_equal(du_candidate, u_prime):
                    log_step(f"U-Sub success (exp rule): u = {u}")
                    return Exp(u)

                # proportional check
                k_const = robust_constant_ratio(du_candidate, u_prime, v)
                if isinstance(k_const, Const):
                    k = k_const.value
                    log_step(f"Proportional U-Sub detected (exp rule): scaled by {k}")
                    return Mul(Const(k), Exp(u))

    log_step("U-Substitution failed.")
    return None


# ------------------------------------------------------------
# Integration by Parts
# ------------------------------------------------------------
def try_integration_by_parts(integrand: Expr, var: Var) -> Optional[Expr]:
    v = var
    log_step(f"Attempting Integration by Parts on {integrand}")

    if isinstance(integrand, Mul):
        for u_candidate, dv_candidate in [(integrand.left, integrand.right),
                                          (integrand.right, integrand.left)]:
            
            # General IBP Rule (u * dv where dv is Exp/Sin/Cos)
            if isinstance(dv_candidate, (Exp, Sin, Cos)):
                u = u_candidate
                dv = dv_candidate
                du = differentiate(u_candidate, v.name)
                
                # FIX: Generalized check for 'u' to include any linear term (c*x) 
                # or a higher-order polynomial (x^n) that we want to reduce.
                is_linear_u = isinstance(du, Const)
                is_higher_poly_u = (isinstance(u, Pow) and 
                                    isinstance(u.base, Var) and 
                                    isinstance(u.exp, Const) and 
                                    u.exp.value >= 1)

                if is_linear_u or is_higher_poly_u:
                    log_step(f"IBP: u={u}, dv={dv}, du={du}")

                    push_depth()
                    v_expr = integrate(dv, v.name, reset=False)
                    pop_depth()

                    log_step(f"IBP inner integration complete: v = {v_expr}")

                    if not isinstance(v_expr, Integrate):
                        uv = Mul(u, v_expr)
                        v_du = Mul(v_expr, du)

                        # Recursively integrate the remaining term (which may require a second IBP)
                        push_depth()
                        integral_v_du = integrate(v_du, v.name, reset=False)
                        pop_depth()

                        # Return IBP result regardless of whether the second integral was solved
                        return Sub(uv, integral_v_du)
                        
    log_step("Integration by Parts failed.")
    return None


# ------------------------------------------------------------
# Main Integration Driver
# ------------------------------------------------------------
def integrate(expr: Expr, var: str, reset: bool = True) -> Expr:
    v = Var(var)
    log_step(f"Integrating expression: {expr}")

    push_depth()

    # CRITICAL FIX: Limit recursion depth to prevent stack overflow on looping integrals
    if get_depth() > 20: 
        log_step("Recursion depth limit reached (20). Returning integral unsolved.")
        pop_depth()
        # Return the expression wrapped in Integrate if it's not already one
        if isinstance(expr, Integrate):
            return expr
        else:
            return Integrate(expr, v)


    # 1. Try U-Substitution first
    u_sub_result = try_u_substitution(expr, v)
    if u_sub_result is not None:
        log_step(f"Returning from U-Substitution: {u_sub_result}")
        pop_depth()
        return rewrite(u_sub_result, simplification_rules())

    # 2. Try Integration by Parts second
    ibp_result = try_integration_by_parts(expr, v)
    if ibp_result is not None:
        log_step(f"Returning from Integration by Parts: {ibp_result}")
        pop_depth()
        return rewrite(ibp_result, simplification_rules())

    # 3. Fallback: rule-based rewrite
    if isinstance(expr, Integrate):
        result = expr
    else:
        result = Integrate(expr, v)
        
    prev = None
    while prev != repr(result):
        prev = repr(result)
        result = rewrite(result, integration_rules(var))
        result = rewrite(result, simplification_rules())

    # 4. Recursively resolve remaining sub-integrals
    def resolve_sub_integrals(expr: Expr) -> Expr:
        # Base Case: Integrate node
        if isinstance(expr, Integrate):
            log_step(f"Recursively integrating sub-term: {expr.expr}")
            original_integrand = expr.expr
            
            push_depth() 
            solved_expr = integrate(original_integrand, var, reset=False)
            pop_depth()
            
            # If the result of the recursive call is still an Integrate 
            # with the original integrand, it means no progress was made. 
            # Return the ORIGINAL Integrate node to stop the loop.
            if isinstance(solved_expr, Integrate) and check_equal(solved_expr.expr, original_integrand):
                 log_step("Integral is structurally equivalent to its unsolved form. Halting sub-recursion.")
                 return expr
            
            return solved_expr
        
        # Recursive Step: Apply to children of all other expression types
        fields = getattr(expr, "__dataclass_fields__", {})
        field_names = list(fields.keys())
        
        new_args = []
        changed = False
        
        for name in field_names:
            val = getattr(expr, name)
            if isinstance(val, Expr):
                new_val = resolve_sub_integrals(val)
                if new_val != val:
                    changed = True
                new_args.append(new_val)
            else:
                new_args.append(val)
                
        return type(expr)(*new_args) if changed else expr

    # Apply the recursive resolver to the current result
    result = resolve_sub_integrals(result)
    
    # Clean up after recursion
    result = rewrite(result, simplification_rules()) 
    
    pop_depth()
    log_step(f"Final integration result: {result}")
    return result


# ------------------------------------------------------------
# DEBUG HARNESS
# ------------------------------------------------------------
if __name__ == "__main__":
    # NOTE: You will need to import 'get_depth' into logger.py for this to run
    # from logger import log_step, reset_log, get_step_counter, LOG_FILE, push_depth, pop_depth, get_depth
    
    print("\n=== Integration Debug Harness (Hierarchical Logger) ===\n")

    x = Var("x")
    tests = [
        ("Combined (x*e^x + cos(x^2)*2x)",
        Add(Mul(x, Exp(x)), Mul(Cos(Pow(x, Const(2))), Mul(Const(2), x)))),

        ("U-Sub: Missing constant factor (x*e^(x^2))",
        Mul(x, Exp(Pow(x, Const(2))))),

        ("U-Sub: sin(x^2)*2x",
        Mul(Sin(Pow(x, Const(2))), Mul(Const(2), x))),

        ("IBP Nested: x^2 * e^x",
        Mul(Pow(x, Const(2)), Exp(x))),

        ("Log Rule variant (2x/(x^2+3))",
        Div(Mul(Const(2), x), Add(Pow(x, Const(2)), Const(3)))),

        ("Future: hyperbolic sqrt(x^2+1) substitution",
        Div(x, Pow(Add(Pow(x, Const(2)), Const(1)), Div(Const(1), Const(2))))),
    ]

    for name, expr in tests:
        reset_log()
        print(f"▶ {name}")
        print(f"Input : {expr}")
        result = integrate(expr, "x")
        print(f"Output: {result}")
        print(f"Total rewrite steps logged: {get_step_counter()}")
        print(f"Log written to: {LOG_FILE}")
        print("-" * 60)