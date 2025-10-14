# ============================================================
# Integration
# ============================================================
from rules import *
from simplification import *
from differentiation import differentiate 
from equality import check_equal           
from typing import Optional

def integration_rules(var: str) -> List[Tuple[Expr, Expr]]:
    """
    Defines the MINIMAL foundational rules for indefinite integration.
    All complex anti-derivatives have been removed to force the use of solvers (like U-Sub, IBP).
    """
    v = Var(var)
    return [
        # --- Linearity (KEEP) ---
        # ∫(u+w)dx = ∫udx + ∫wdx
        (Integrate(Add(PatternVar("u"), PatternVar("w")), v),
         Add(Integrate(PatternVar("u"), v), Integrate(PatternVar("w"), v))),
        # ∫(c*u)dx = c * ∫udx
        (Integrate(Mul(Const(PatternVar("c")), PatternVar("u")), v),
         Mul(Const(PatternVar("c")), Integrate(PatternVar("u"), v))),

        # --- Basic Anti-derivatives (KEEP as foundational building blocks) ---
        # ∫0dx = 0
        (Integrate(Const(0), v), Const(0)),
        # ∫cdx = c*x
        (Integrate(Const(PatternVar("c")), v), Mul(Const(PatternVar("c")), v)),
        
        # --- Power Rule (∫x^n dx = x^(n+1)/(n+1), n != -1) (KEEP) ---
        (Integrate(Pow(v, Const(PatternVar("n"))), v),
         Div(Pow(v, Add(Const(PatternVar("n")), Const(1))),
             Add(Const(PatternVar("n")), Const(1)))),

        # --- Exponential & Trig ---
        # ∫e^x dx = e^x
        (Integrate(Exp(v), v), Exp(v)),
        # ∫cos(x) dx = sin(x)
        (Integrate(Cos(v), v), Sin(v)),
        # ∫sin(x) dx = -cos(x)
        (Integrate(Sin(v), v), Neg(Cos(v))),
    ]

def try_u_substitution(integrand: Expr, var: Var) -> Optional[Expr]:
    """
    Attempts to solve the integral ∫ f(u(x)) * u'(x) dx = F(u(x)).
    Now includes the Logarithmic case: ∫ u'/u dx = ln|u|
    """
    v = var
    
    # --- Case E: Logarithmic Integration (∫ u'/u dx = ln|u|) ---
    if isinstance(integrand, Div):
        u = integrand.right # Denominator is u
        u_prime = differentiate(u, v.name)
        
        # Check if the numerator is the derivative of the denominator
        if check_equal(integrand.left, u_prime):
            # Found u-sub: ∫ u'/u du = Log(|u|). We will use Log(u) for simplicity
            return Log(u)

    # Now check for product forms (f(u) * u')
    if isinstance(integrand, Mul):
        for f_u_candidate, du_candidate in [(integrand.left, integrand.right), (integrand.right, integrand.left)]:
            
            # --- Case A: f(u) = Power, u^n (n != -1) ---
            if isinstance(f_u_candidate, Pow) and isinstance(f_u_candidate.exp, Const):
                if f_u_candidate.exp.value == -1: # Skip n=-1, handled by Log rule above
                    continue
                
                u = f_u_candidate.base
                n = f_u_candidate.exp
                u_prime = differentiate(u, v.name)
                if check_equal(du_candidate, u_prime):
                    # Found u-sub: ∫ u^n du = u^(n+1)/(n+1)
                    return Div(Pow(u, Add(n, Const(1))), Add(n, Const(1)))

            # --- Case B: f(u) = Cosine ---
            if isinstance(f_u_candidate, Cos):
                u = f_u_candidate.arg
                u_prime = differentiate(u, v.name)
                if check_equal(du_candidate, u_prime):
                    # Found u-sub: ∫ cos(u) du = sin(u)
                    return Sin(u)

            # --- Case C: f(u) = Sine ---
            if isinstance(f_u_candidate, Sin):
                u = f_u_candidate.arg
                u_prime = differentiate(u, v.name)
                if check_equal(du_candidate, u_prime):
                    # Found u-sub: ∫ sin(u) du = -cos(u)
                    return Neg(Cos(u))

            # --- Case D: f(u) = Exponential ---
            if isinstance(f_u_candidate, Exp):
                u = f_u_candidate.arg
                u_prime = differentiate(u, v.name)
                if check_equal(du_candidate, u_prime):
                    # Found u-sub: ∫ exp(u) du = exp(u)
                    return Exp(u)

    return None # No substitution found

def try_integration_by_parts(integrand: Expr, var: Var) -> Optional[Expr]:
    """
    Attempts to solve ∫ u dv using the formula uv - ∫ v du.
    Uses a simple heuristic: u = x, dv = transcendental function (exp, sin, cos).
    """
    v = var
    
    if isinstance(integrand, Mul):
        
        # Heuristic: Find a term to differentiate (u) that simplifies (like x)
        for u_candidate, dv_candidate in [(integrand.left, integrand.right), (integrand.right, integrand.left)]:
            
            # Simple Case: u = x
            if check_equal(u_candidate, v):
                u = u_candidate
                dv = dv_candidate
                
                # Check if dv is something we can easily integrate (exp, sin, cos)
                if isinstance(dv, (Exp, Sin, Cos)):
                    # 1. Calculate du = differentiate(u)
                    du = differentiate(u, v.name) 
                    
                    # 2. Calculate v = integrate(dv)
                    # Recursively integrate dv. This relies on foundational rules.
                    v_expr = integrate(dv, v.name) 
                    
                    # Check if integration was successful (i.e., didn't return an unresolved integral)
                    if not isinstance(v_expr, Integrate):
                        # Formula: u*v - integral(v*du)
                        uv = Mul(u, v_expr)
                        v_du = Mul(v_expr, du)
                        
                        # Recursively call integrate on the new term ∫ v du
                        integral_v_du = integrate(v_du, v.name)
                        
                        # Check if the recursive integral was successful
                        if not isinstance(integral_v_du, Integrate):
                            # The entire integral is solved: u*v - ∫v du
                            return Sub(uv, integral_v_du)

    return None

def integrate(expr: Expr, var: str) -> Expr:
    """
    Applies solvers (U-Sub, IBP), then foundational rules, and finally simplification iteratively.
    """
    reset_log()
    v = Var(var)
    
    # 1. Try U-Substitution (Logarithmic Rule included here)
    u_sub_result = try_u_substitution(expr, v)
    if u_sub_result is not None:
        return rewrite(u_sub_result, simplification_rules()) 

    # 2. Try Integration by Parts (IBP)
    ibp_result = try_integration_by_parts(expr, v)
    if ibp_result is not None:
        return rewrite(ibp_result, simplification_rules())

    # 3. If solvers fail, proceed with the standard rewrite engine (for basic rules)
    result = Integrate(expr, v)
    
    prev = None
    while prev != repr(result):
        prev = repr(result)
        # Apply direct anti-derivative and linearity rules
        result = rewrite(result, integration_rules(var))
        # Simplify the expression after each rule application
        result = rewrite(result, simplification_rules())

    return result