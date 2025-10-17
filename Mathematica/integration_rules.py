# integration_rules.py
# Foundational integration rules for linearity and elementary antiderivatives.

from rules import Expr, Var, Integrate, Add, Mul, Const, Div, Pow, Exp, Cos, Sin, Neg, PatternVar, Log, Abs, Sinh, Cosh, Tan, ArcTan, Sec, ArcSin, Sub

def integration_rules(var: str) -> list[tuple[Expr, Expr]]:
    """Foundational integration rules for linearity and elementary antiderivatives."""
    v = Var(var)
    n = PatternVar("n") # Use a single PatternVar instance for consistency
    c = PatternVar("c")
    u = PatternVar("u")
    w = PatternVar("w")
    
    # Define helper variables for generalized inverse trig rules
    a_sq = PatternVar("a_sq") 
    a = Pow(Const(a_sq), Div(Const(1), Const(2))) # Represents sqrt(a^2)

    return [
        # --- Linearity ---
        (Integrate(Add(u, w), v), Add(Integrate(u, v), Integrate(w, v))),
        (Integrate(Mul(Const(c), u), v), Mul(Const(c), Integrate(u, v))),
        (Integrate(Neg(u), v), Neg(Integrate(u, v))),

        # --- Constants ---
        (Integrate(Const(0), v), Const(0)),
        (Integrate(Const(c), v), Mul(Const(c), v)),

        # --- Log Rule (n = -1, MUST BE FIRST) ---
        (Integrate(Pow(v, Const(-1)), v), Log(Abs(v))),
        
        # --- CRITICAL FIX 1: Power Rule for Negative Integers (via Negation) ---
        # Matches Pow(x, Neg(Const(n))), which is the output of 1/x^n -> x^-n
        # Example: x^-3 is matched by Neg(Const(n)) where n=3.
        (Integrate(Pow(v, Neg(Const(n))), v),
         Div(Pow(v, Add(Neg(Const(n)), Const(1))),
             Add(Neg(Const(n)), Const(1)))),

        # --- CRITICAL FIX 2: Power Rule (General case, handles x^3) ---
        # Matches Pow(x, Const(n)), where n is any number (positive or negative)
        (Integrate(Pow(v, Const(n)), v),
         Div(Pow(v, Add(Const(n), Const(1))),
             Add(Const(n), Const(1)))),

        # --- Exponential & Trig ---
        (Integrate(Exp(v), v), Exp(v)),
        (Integrate(Cos(v), v), Sin(v)),
        (Integrate(Sin(v), v), Neg(Cos(v))),

        # --- Hyperbolic Functions (Direct Rules) ---
        (Integrate(Sinh(v), v), Cosh(v)),
        (Integrate(Cosh(v), v), Sinh(v)),

        # --- Trig Antiderivative Seeds (sec^2) ---
        (Integrate(Pow(Sec(v), Const(2)), v), Tan(v)),

        # --- Inverse Trig (ArcTan: 1/(a^2+x^2)) ---
        (Integrate(Div(Const(1), Add(Const(a_sq), Pow(v, Const(2)))), v),
         Mul(Div(Const(1), a), ArcTan(Div(v, a)))),

        # --- Inverse Trig (ArcSin: 1/sqrt(a^2-x^2)) ---
        (Integrate(Div(Const(1), Pow(Sub(Const(a_sq), Pow(v, Const(2))), Div(Const(1), Const(2)))), v),
         ArcSin(Div(v, a))),
    ]