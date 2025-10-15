# integration_strategies.py
# U-Substitution and Integration by Parts strategies.

from typing import Optional, Callable
from rules import Expr, Var, Const, Add, Mul, Div, Pow, Exp, Cos, Sin, Neg, Log, Sub, Integrate, rewrite
from simplification import simplification_rules, evaluate_constants
from differentiation import differentiate
from equality import check_equal
from logger import log_step, push_depth, pop_depth

# Define the expected signature for the integrate function for IBP
IntegrateFunc = Callable[[Expr, str, bool], Expr]

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
        
        if isinstance(u_prime, Const) and u_prime.value != 0:
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

            # Power Rule 
            if isinstance(f_u_candidate, Pow) and isinstance(f_u_candidate.exp, Const):
                if f_u_candidate.exp.value == -1: continue
                u = f_u_candidate.base
                n = f_u_candidate.exp
                u_prime = differentiate(u, v.name)
                
                # proportional u' check
                k_const = robust_constant_ratio(du_candidate, u_prime, v)
                if isinstance(k_const, Const):
                    log_step(f"Proportional U-Sub detected (power rule): scaled by {k_const.value}")
                    result = Mul(k_const, Div(Pow(u, Add(n, Const(1))), Add(n, Const(1))))
                    return evaluate_constants(result)

            # Trig and Exponential
            if isinstance(f_u_candidate, Cos):
                u = f_u_candidate.arg
                u_prime = differentiate(u, v.name)
                k_const = robust_constant_ratio(du_candidate, u_prime, v)
                if isinstance(k_const, Const): return Mul(k_const, Sin(u))

            if isinstance(f_u_candidate, Sin):
                u = f_u_candidate.arg
                u_prime = differentiate(u, v.name)
                k_const = robust_constant_ratio(du_candidate, u_prime, v)
                if isinstance(k_const, Const): return Mul(k_const, Neg(Cos(u)))

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
def is_poly_or_power(expr: Expr, var_name: str) -> bool:
    """
    Helper to determine if an expression is a polynomial, a power of the variable, 
    or a constant multiple of one (e.g., x, x^n, 2*x).
    """
    
    # Base cases: Var (x) or Power of Var (x^n)
    if isinstance(expr, Var) and expr.name == var_name:
        return True
    if isinstance(expr, Pow) and isinstance(expr.base, Var) and expr.base.name == var_name and isinstance(expr.exp, Const):
        return True
    
    # Handle constant multipliers
    if isinstance(expr, Mul):
        left, right = expr.left, expr.right
        
        if isinstance(left, Const):
            return is_poly_or_power(right, var_name) 
        if isinstance(right, Const):
            return is_poly_or_power(left, var_name) 

    return False

def try_integration_by_parts(integrand: Expr, var: Var, integrate_fn: IntegrateFunc) -> Optional[Expr]:
    v = var
    log_step(f"Attempting Integration by Parts on {integrand}")
    var_name = v.name

    if isinstance(integrand, Mul):
        
        # We will try two pairings: (A, B) and (B, A)
        for u_candidate, dv_candidate in [(integrand.left, integrand.right),
                                             (integrand.right, integrand.left)]:
            
            # --- IBP HEURISTIC (L-I-A-T-E for u) ---
            # 1. u = Log (L), dv = Algebraic (A) or any power 
            is_log_u_case = isinstance(u_candidate, Log) and (is_poly_or_power(dv_candidate, var_name) or isinstance(dv_candidate, Const))
            
            # 2. u = Algebraic (A), dv = Trig (T) or Exponential (E) 
            is_poly_u_case = is_poly_or_power(u_candidate, var_name) and isinstance(dv_candidate, (Exp, Sin, Cos))

            if is_log_u_case or is_poly_u_case:
                u = u_candidate
                dv = dv_candidate
                du = differentiate(u_candidate, var_name)
                
                # Check for u to be of a type that reduces complexity (x^n, ln(x))
                is_reducable = (isinstance(du, Const) or 
                                (isinstance(u, Pow) and isinstance(u.base, Var) and u.exp.value > 0) or
                                is_log_u_case)

                if is_reducable:
                    log_step(f"IBP selection: u={u}, dv={dv}, du={du}")

                    push_depth()
                    # Calculate v = ∫dv dx using the provided integrate function
                    v_expr = integrate_fn(dv, var_name, reset=False) 
                    pop_depth()

                    if not isinstance(v_expr, Integrate):
                        log_step(f"IBP inner integration succeeded: v = {v_expr}")
                        uv = Mul(u, v_expr)
                        v_du = Mul(v_expr, du) # The integral part: ∫ v du dx

                        # CRITICAL FIX: Simplify the integral term before recursive integration
                        v_du = rewrite(v_du, simplification_rules())
                        v_du = evaluate_constants(v_du)
                        log_step(f"Simplified integral part (v*du): {v_du}")
                        
                        # Recursively solve the remaining integral ∫ v du dx
                        push_depth()
                        integral_v_du = integrate_fn(v_du, var_name, reset=False)
                        pop_depth()

                        # Return u*v - ∫ v*du dx
                        return Sub(uv, integral_v_du)
                        
    log_step("Integration by Parts failed.")
    return None