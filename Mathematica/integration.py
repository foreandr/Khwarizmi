# ============================================================
# Integration
# ============================================================
from rules import *
from simplification import *

def integration_rules(var: str) -> List[Tuple[Expr, Expr]]:
    """Defines the basic rules for indefinite integration."""
    v = Var(var)
    return [
        # --- Linearity ---
        # ∫(u+w)dx = ∫udx + ∫wdx
        (Integrate(Add(PatternVar("u"), PatternVar("w")), v),
         Add(Integrate(PatternVar("u"), v), Integrate(PatternVar("w"), v))),
        # ∫(c*u)dx = c * ∫udx
        (Integrate(Mul(Const(PatternVar("c")), PatternVar("u")), v),
         Mul(Const(PatternVar("c")), Integrate(PatternVar("u"), v))),

        # --- Basic Rules ---
        # ∫0dx = 0
        (Integrate(Const(0), v), Const(0)),
        # ∫cdx = c*x
        (Integrate(Const(PatternVar("c")), v), Mul(Const(PatternVar("c")), v)),
        
        # --- Power Rule (∫x^n dx = x^(n+1)/(n+1), n != -1) ---
        (Integrate(Pow(v, Const(PatternVar("n"))), v),
         Div(Pow(v, Add(Const(PatternVar("n")), Const(1))),
             Add(Const(PatternVar("n")), Const(1)))),

        # --- Logarithmic Rule (∫x^-1 dx = ln(|x|)) ---
        (Integrate(Div(Const(1), v), v),
         Log(v)), # Using Log(v) for ln(|x|) for simplicity initially

        # --- Exponential Rule ---
        # ∫e^x dx = e^x
        (Integrate(Exp(v), v), Exp(v)),
        
        # --- Trigonometric Rules ---
        # ∫cos(x) dx = sin(x)
        (Integrate(Cos(v), v), Sin(v)),
        # ∫sin(x) dx = -cos(x)
        (Integrate(Sin(v), v), Neg(Cos(v))),
    ]

def integrate(expr: Expr, var: str) -> Expr:
    """
    Applies integration rules and simplification iteratively.
    NOTE: The Constant of Integration (+C) is omitted for now for simplicity.
    """
    reset_log()
    v = Var(var)
    
    result = Integrate(expr, v)
    
    prev = None
    while prev != repr(result):
        prev = repr(result)
        # We rewrite the integral expression itself using the integration rules
        result = rewrite(result, integration_rules(var))
        # We simplify the *result* of any integration step
        result = rewrite(result, simplification_rules())

    return result