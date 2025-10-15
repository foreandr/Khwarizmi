# integration_rules.py
# Foundational integration rules for linearity and elementary antiderivatives.

from rules import Expr, Var, Integrate, Add, Mul, Const, Div, Pow, Exp, Cos, Sin, Neg, PatternVar

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