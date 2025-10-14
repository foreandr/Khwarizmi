# ============================================================
# integration.py — Hierarchical Integration Engine (FINAL FIX V5)
# ============================================================

from rules import *
from simplification import *
from differentiation import differentiate
from equality import check_equal
# CRITICAL FIX: Ensure get_depth is imported
from logger import log_step, reset_log, get_step_counter, LOG_FILE, push_depth, pop_depth, get_depth 
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
        
        # --- Negation Linearity (CRITICAL FIX for IBP cleanup) ---
        (Integrate(Neg(PatternVar("u")), v), 
         Neg(Integrate(PatternVar("u"), v))),

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
# U-Substitution Helper and Main Function
# ------------------------------------------------------------

def robust_constant_ratio(numerator: Expr, denominator: Expr, var: Var) -> Optional[Const]:
    """
    Calculates the ratio k = numerator / denominator and returns it as a Const.
    """
    
    # 1. Try algebraic cancellation using rewrite engine first
    ratio = Div(numerator, denominator)
    prev_ratio = None
    while prev_ratio != repr(ratio):
        prev_ratio = repr(ratio)
        ratio = rewrite(ratio, simplification_rules())
        ratio = evaluate_constants(ratio) 
    
    if isinstance(ratio, Const):
        return ratio

    # 2. Heuristic Check for (f(x) / (c * f(x))) or (c * f(x) / f(x))
    
    # Check if the denominator is of the form c * f(x)
    if isinstance(denominator, Mul):
        for c_const, f_x in [(denominator.left, denominator.right), (denominator.right, denominator.left)]:
            if isinstance(c_const, Const):
                if check_equal(numerator, f_x):
                    return evaluate_constants(Div(Const(1), c_const))

    # Check if the numerator is of the form c * f(x)
    if isinstance(numerator, Mul):
        for c_const, f_x in [(numerator.left, numerator.right), (numerator.right, numerator.left)]:
            if isinstance(c_const, Const):
                if check_equal(denominator, f_x):
                    return c_const
                    
    # Special case: check for Negation (f(x) / -f(x) or -f(x) / f(x))
    if isinstance(denominator, Neg) and check_equal(numerator, denominator.arg):
        return Const(-1.0)
    if isinstance(numerator, Neg) and check_equal(denominator, numerator.arg):
        return Const(-1.0)
    
    return None

def try_u_substitution(integrand: Expr, var: Var) -> Optional[Expr]:
    v = var
    log_step(f"Attempting U-Substitution on {integrand}")

    # --- Standalone f(u) case: ∫ f(u) dx, where u' is a constant C ---
    if isinstance(integrand, (Sin, Cos, Exp)):
        u = integrand.arg
        u_prime = differentiate(u, v.name)
        
        if isinstance(u_prime, Const):
            k = 1 / u_prime.value
            log_step(f"Linear U-Sub detected: u={u}, u'={u_prime.value}, scaled by {k}")
            
            k_const = Const(k) 
            
            if isinstance(integrand, Sin):
                return Mul(k_const, Neg(Cos(u))) 
            if isinstance(integrand, Cos):
                return Mul(k_const, Sin(u))    
            if isinstance(integrand, Exp):
                return Mul(k_const, Exp(u))    

    # --- Logarithmic case: ∫ u'/u dx = ln|u| ---
    if isinstance(integrand, Div):
        u = integrand.right
        u_prime = differentiate(u, v.name)
        
        # proportional u'-multiplier check
        k_const = robust_constant_ratio(integrand.left, u_prime, v)
        if isinstance(k_const, Const):
            log_step(f"Proportional U-Sub detected (log rule): scaled by {k_const.value}")
            return Mul(k_const, Log(u))

    # --- f(u)*u' case ---
    if isinstance(integrand, Mul):
        for f_u_candidate, du_candidate in [(integrand.left, integrand.right),
                                             (integrand.right, integrand.left)]:

            # Power Rule (Handles Challenge 1: x^2 * (x^3+5)^-4)
            if isinstance(f_u_candidate, Pow) and isinstance(f_u_candidate.exp, Const):
                if f_u_candidate.exp.value == -1: continue
                u = f_u_candidate.base
                n = f_u_candidate.exp
                u_prime = differentiate(u, v.name)
                
                # proportional u' check
                k_const = robust_constant_ratio(du_candidate, u_prime, v)
                if isinstance(k_const, Const):
                    log_step(f"Proportional U-Sub detected (power rule): scaled by {k_const.value}")
                    # Ensure constant evaluation happens on the factor before return
                    result = Mul(k_const, Div(Pow(u, Add(n, Const(1))), Add(n, Const(1))))
                    return evaluate_constants(result)

            # Cosine
            if isinstance(f_u_candidate, Cos):
                u = f_u_candidate.arg
                u_prime = differentiate(u, v.name)
                k_const = robust_constant_ratio(du_candidate, u_prime, v)
                if isinstance(k_const, Const): return Mul(k_const, Sin(u))

            # Sine
            if isinstance(f_u_candidate, Sin):
                u = f_u_candidate.arg
                u_prime = differentiate(u, v.name)
                k_const = robust_constant_ratio(du_candidate, u_prime, v)
                if isinstance(k_const, Const): return Mul(k_const, Neg(Cos(u)))

            # Exponential
            if isinstance(f_u_candidate, Exp):
                u = f_u_candidate.arg
                u_prime = differentiate(u, v.name)
                k_const = robust_constant_ratio(du_candidate, u_prime, v)
                if isinstance(k_const, Const): return Mul(k_const, Exp(u))

    log_step("U-Substitution failed.")
    return None


# ------------------------------------------------------------
# Integration by Parts
# ------------------------------------------------------------
def try_integration_by_parts(integrand: Expr, var: Var) -> Optional[Expr]:
    v = var
    log_step(f"Attempting Integration by Parts on {integrand}")

    if isinstance(integrand, Mul):
        
        # FIXED: Updated to correctly identify (Const * Poly) terms like 2*x
        def is_poly_or_power(expr):
            # Base cases: Var (x) or Power of Var (x^n)
            if isinstance(expr, Var):
                return True
            if isinstance(expr, Pow) and isinstance(expr.base, Var) and isinstance(expr.exp, Const):
                return True
            
            # CRITICAL FIX: Handle constant multipliers like (2*x) or (x^2*3) by recursing on the non-constant part.
            if isinstance(expr, Mul):
                left, right = expr.left, expr.right
                # If one is a Const, check if the other is a polynomial/power
                if isinstance(left, Const):
                    return is_poly_or_power(right) 
                if isinstance(right, Const):
                    return is_poly_or_power(left) 

            return False

        # We will try two pairings: (A, B) and (B, A)
        for u_candidate, dv_candidate in [(integrand.left, integrand.right),
                                             (integrand.right, integrand.left)]:
            
            # --- IBP HEURISTIC (L-I-A-T-E for u) ---
            
            # 1. u = Log (L), dv = Algebraic (A) or any power (FIXED for x*ln(x))
            is_log_u_case = isinstance(u_candidate, Log) and (is_poly_or_power(dv_candidate) or isinstance(dv_candidate, Const))
            
            # 2. u = Algebraic (A), dv = Trig (T) or Exponential (E) (Original passing case)
            is_poly_u_case = is_poly_or_power(u_candidate) and isinstance(dv_candidate, (Exp, Sin, Cos))

            if is_log_u_case or is_poly_u_case:
                u = u_candidate
                dv = dv_candidate
                du = differentiate(u_candidate, v.name)
                
                # Check for u to be of a type that reduces complexity (x^n, ln(x))
                is_reducable = (isinstance(du, Const) or 
                                (isinstance(u, Pow) and isinstance(u.base, Var) and u.exp.value > 0) or
                                is_log_u_case)

                if is_reducable:
                    log_step(f"IBP selection: u={u}, dv={dv}, du={du}")

                    push_depth()
                    # Calculate v = ∫dv dx
                    v_expr = integrate(dv, v.name, reset=False) 
                    pop_depth()

                    if not isinstance(v_expr, Integrate):
                        log_step(f"IBP inner integration succeeded: v = {v_expr}")
                        uv = Mul(u, v_expr)
                        v_du = Mul(v_expr, du) # The integral part: ∫ v du dx

                        # --- CRITICAL FIX: Simplify the integral term before recursive integration ---
                        v_du = rewrite(v_du, simplification_rules())
                        v_du = evaluate_constants(v_du)
                        log_step(f"Simplified integral part (v*du): {v_du}")
                        # --- END FIX ---
                        
                        # Recursively solve the remaining integral ∫ v du dx
                        push_depth()
                        integral_v_du = integrate(v_du, v.name, reset=False)
                        pop_depth()

                        return Sub(uv, integral_v_du)
                        
    log_step("Integration by Parts failed.")
    return None


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
    ibp_result = try_integration_by_parts(expr, v)
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
    # Note: You may need to import Sinh, ArcTan, etc. from rules.py if they aren't already.

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
            # ∫ 5 dx = 5x
            "Basic: Constant (5)",
            Const(5)
        ),
        (
            # ∫ x^3 dx = x^4 / 4
            "Basic: Power Rule (x^3)",
            Pow(x, Const(3))
        ),
        (
            # ∫ 1/x^3 dx = ∫ x^-3 dx = -1/(2x^2)
            "Basic: Negative Power (1/x^3)",
            Div(Const(1), Pow(x, Const(3)))
        ),
        (
            # ∫ 1/sqrt(x) dx = ∫ x^-0.5 dx = 2*sqrt(x)
            "Basic: Fractional Power (1/sqrt(x))",
            Pow(x, Div(Const(-1), Const(2)))
        ),
        (
            # ∫ cos(x) dx = sin(x)
            "Basic: Simple Trig (cos(x))",
            Cos(x)
        ),

        # ----------------------------------------------------------------------
        # --- NEW INTEGRATION BY PARTS (IBP) TESTS ---
        # ----------------------------------------------------------------------
        (
            # ∫ x * e^x dx = x*e^x - e^x
            "IBP Simple: x*e^x (Standalone)",
            Mul(x, Exp(x))
        ),
        (
            # ∫ ln(x) dx = x*ln(x) - x
            "IBP Log: ln(x)",
            Log(x)
        ),
        (
            # ∫ x * cos(x) dx = x*sin(x) + cos(x)
            "IBP Simple: x*cos(x)",
            Mul(x, Cos(x))
        ),
        
        # ----------------------------------------------------------------------
        # --- NEW U-SUBSTITUTION TESTS ---
        # ----------------------------------------------------------------------
        (
            # ∫ e^(3x) dx = 1/3 * e^(3x) (Linear U-Sub)
            "U-Sub: Linear Exponential (e^3x)",
            Exp(Mul(Const(3), x))
        ),
        (
            # ∫ x/(x^2+1) dx = 1/2 * ln(x^2+1) (Missing Constant Log Rule)
            "U-Sub: Missing Factor Log (x/(x^2+1))",
            Div(x, Add(Pow(x, Const(2)), Const(1)))
        ),
        (
            # ∫ cos^3(x)*sin(x) dx = -1/4 * cos^4(x)
            "U-Sub: Trig Power (cos^3(x)*sin(x))",
            Mul(Pow(Cos(x), Const(3)), Sin(x))
        ),
        (
            # ∫ 1/((x+1)^(0.5)) dx = 2*sqrt(x+1)
            "U-Sub: Complex Fractional Power",
            Pow(Add(x, Const(1)), Div(Const(-1), Const(2)))
        ),
        (
            # ∫ (ln(x))/x dx = 1/2 * ln(x)^2
            "U-Sub: Nested Log Power (ln(x)/x)",
            Div(Log(x), x)
        ),
        
        # ----------------------------------------------------------------------
        # --- NEW SPECIAL FUNCTION TESTS ---
        # ----------------------------------------------------------------------
        (
            # ∫ 1/(1+x^2) dx = arctan(x) (Requires the arctan rule)
            "Special: Inverse Trig (1/(1+x^2))",
            Div(Const(1), Add(Const(1), Pow(x, Const(2))))
        ),
        (
            # ∫ sinh(x) dx = cosh(x) (Requires Hyperbolic rule)
            "Basic: Hyperbolic (sinh(x))",
            Sinh(x) # Requires 'from rules import Sinh' or similar
        ),
        (
            # ∫ sec^2(2x) dx = 1/2 * tan(2x) (U-Sub on standard rule)
            "U-Sub: Trig Identity (sec^2(2x))",
            Pow(Sec(Mul(Const(2), x)), Const(2)) # Requires 'from rules import Sec'
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