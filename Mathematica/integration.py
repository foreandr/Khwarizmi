# ============================================================
# integration.py — Hierarchical Integration Engine
# ============================================================

from rules import *
from simplification import *
from differentiation import differentiate
from equality import check_equal
from logger import log_step, reset_log, get_step_counter, LOG_FILE, push_depth, pop_depth
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
    ]


# ------------------------------------------------------------
# U-Substitution
# ------------------------------------------------------------
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

            # Cosine
            if isinstance(f_u_candidate, Cos):
                u = f_u_candidate.arg
                u_prime = differentiate(u, v.name)
                if check_equal(du_candidate, u_prime):
                    log_step(f"U-Sub success (cos rule): u = {u}")
                    return Sin(u)

            # Sine
            if isinstance(f_u_candidate, Sin):
                u = f_u_candidate.arg
                u_prime = differentiate(u, v.name)
                if check_equal(du_candidate, u_prime):
                    log_step(f"U-Sub success (sin rule): u = {u}")
                    return Neg(Cos(u))

            # Exponential
            if isinstance(f_u_candidate, Exp):
                u = f_u_candidate.arg
                u_prime = differentiate(u, v.name)
                if check_equal(du_candidate, u_prime):
                    log_step(f"U-Sub success (exp rule): u = {u}")
                    return Exp(u)

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
            if check_equal(u_candidate, v):
                u = u_candidate
                dv = dv_candidate

                if isinstance(dv, (Exp, Sin, Cos)):
                    du = differentiate(u, v.name)
                    log_step(f"IBP: u={u}, dv={dv}, du={du}")

                    push_depth()
                    v_expr = integrate(dv, v.name, reset=False)
                    pop_depth()

                    log_step(f"IBP inner integration complete: v = {v_expr}")

                    if not isinstance(v_expr, Integrate):
                        uv = Mul(u, v_expr)
                        v_du = Mul(v_expr, du)

                        push_depth()
                        integral_v_du = integrate(v_du, v.name, reset=False)
                        pop_depth()

                        if not isinstance(integral_v_du, Integrate):
                            log_step(f"IBP success: u={u}, v={v_expr}")
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
    result = Integrate(expr, v)
    prev = None
    while prev != repr(result):
        prev = repr(result)
        result = rewrite(result, integration_rules(var))
        result = rewrite(result, simplification_rules())

    # 4. Recursively resolve remaining sub-integrals
    if isinstance(result, Add):
        new_terms = []
        for term in [result.left, result.right]:
            if isinstance(term, Integrate):
                log_step(f"Recursively integrating sub-term: {term.expr}")
                push_depth()
                new_terms.append(integrate(term.expr, var, reset=False))
                pop_depth()
            else:
                new_terms.append(term)
        result = Add(*new_terms)

    pop_depth()
    log_step(f"Final integration result: {result}")
    return result


# ------------------------------------------------------------
# DEBUG HARNESS
# ------------------------------------------------------------
if __name__ == "__main__":
    reset_log()
    print("\n=== Integration Debug Harness (Hierarchical Logger) ===\n")

    x = Var("x")
    tests = [
        ("Combined (x*e^x + cos(x^2)*2x)",
         Add(Mul(x, Exp(x)), Mul(Cos(Pow(x, Const(2))), Mul(Const(2), x)))),
    ]

    for name, expr in tests:
        print(f"▶ {name}")
        print(f"Input : {expr}")
        result = integrate(expr, "x")
        # input("--")
        print(f"Output: {result}")
        print(f"Total rewrite steps logged: {get_step_counter()}")
        print(f"Log written to: {LOG_FILE}")
        print("-" * 60)
