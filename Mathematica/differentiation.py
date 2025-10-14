# ============================================================
# Differentiation
# ============================================================
from rules import *
from simplification import *

def differentiate(expr: Expr, var: str) -> Expr:
    v = Var(var)
    
    # Placeholder for |u| using Pow for square root of u^2
    def Abs(u):
        return Pow(Pow(u, Const(2)), Div(Const(1), Const(2)))

    diff_rules = [
        # constants and variables
        (Differentiate(Const(PatternVar("c")), Var(PatternVar("vv"))), Const(0)),
        (Differentiate(Var(var), Var(var)), Const(1)),
        (Differentiate(Var(PatternVar("x")), Var(var)), Const(0)),

        # linearity
        (Differentiate(Add(PatternVar("u"), PatternVar("w")), Var(var)),
            Add(Differentiate(PatternVar("u"), Var(var)), Differentiate(PatternVar("w"), Var(var)))),
        (Differentiate(Sub(PatternVar("u"), PatternVar("w")), Var(var)),
            Sub(Differentiate(PatternVar("u"), Var(var)), Differentiate(PatternVar("w"), Var(var)))),
        (Differentiate(Mul(Const(PatternVar("c")), PatternVar("u")), Var(var)),
            Mul(Const(PatternVar("c")), Differentiate(PatternVar("u"), Var(var)))),

        # product / quotient
        (Differentiate(Mul(PatternVar("u"), PatternVar("w")), Var(var)),
            Add(Mul(Differentiate(PatternVar("u"), Var(var)), PatternVar("w")),
                Mul(PatternVar("u"), Differentiate(PatternVar("w"), Var(var))))),
        (Differentiate(Div(PatternVar("u"), PatternVar("w")), Var(var)),
            Div(Sub(Mul(Differentiate(PatternVar("u"), Var(var)), PatternVar("w")),
                      Mul(PatternVar("u"), Differentiate(PatternVar("w"), Var(var)))),
                Pow(PatternVar("w"), Const(2)))),

        # --- Power Rules (Specific to General) ---
        # Constant Power Rule: d/dx(u^n) = n * u^(n-1) * u'
        (Differentiate(Pow(PatternVar("u"), Const(PatternVar("n"))), Var(var)),
            Mul(Const(PatternVar("n")),
                Mul(Pow(PatternVar("u"), Sub(Const(PatternVar("n")), Const(1))),
                    Differentiate(PatternVar("u"), Var(var))))),
        
        # General Power Rule: d/dx(u^w) = u^w * [ w' * ln(u) + w * (u'/u) ]
        (Differentiate(Pow(PatternVar("u"), PatternVar("w")), Var(var)),
            Mul(Pow(PatternVar("u"), PatternVar("w")),
                Add(Mul(Differentiate(PatternVar("w"), Var(var)), Log(PatternVar("u"))),
                    Mul(PatternVar("w"), Div(Differentiate(PatternVar("u"), Var(var)), PatternVar("u")))))),

        # exp / log
        (Differentiate(Exp(PatternVar("u")), Var(var)),
            Mul(Exp(PatternVar("u")), Differentiate(PatternVar("u"), Var(var)))),
        (Differentiate(Log(PatternVar("u")), Var(var)),
            Div(Differentiate(PatternVar("u"), Var(var)), PatternVar("u"))),

        # trig
        (Differentiate(Sin(PatternVar("u")), Var(var)),
            Mul(Cos(PatternVar("u")), Differentiate(PatternVar("u"), Var(var)))),
        (Differentiate(Cos(PatternVar("u")), Var(var)),
            Mul(Const(-1), Mul(Sin(PatternVar("u")), Differentiate(PatternVar("u"), Var(var))))),
        (Differentiate(Tan(PatternVar("u")), Var(var)),
            Mul(Div(Const(1), Pow(Cos(PatternVar("u")), Const(2))), Differentiate(PatternVar("u"), Var(var)))),
        (Differentiate(Sec(PatternVar("u")), Var(var)),
        Mul(Sec(PatternVar("u")),
            Mul(Tan(PatternVar("u")),
                Differentiate(PatternVar("u"), Var(var))))),
        (Differentiate(Csc(PatternVar("u")), Var(var)),
        Neg(Mul(Csc(PatternVar("u")),
                Mul(Cot(PatternVar("u")),
                    Differentiate(PatternVar("u"), Var(var)))))),
        (Differentiate(Cot(PatternVar("u")), Var(var)),
        Neg(Mul(Div(Const(1), Pow(Sin(PatternVar("u")), Const(2))),
                Differentiate(PatternVar("u"), Var(var))))),
        
        # ----- Inverse Trig (Completed Set) -----
        (Differentiate(ArcSin(PatternVar("u")), Var(var)),
            Div(Differentiate(PatternVar("u"), Var(var)),
                Pow(Sub(Const(1), Pow(PatternVar("u"), Const(2))),
                    Div(Const(1), Const(2))))), 
        (Differentiate(ArcCos(PatternVar("u")), Var(var)),
            Neg(Div(Differentiate(PatternVar("u"), Var(var)),
                Pow(Sub(Const(1), Pow(PatternVar("u"), Const(2))),
                    Div(Const(1), Const(2)))))), 
        (Differentiate(ArcTan(PatternVar("u")), Var(var)),
            Div(Differentiate(PatternVar("u"), Var(var)),
                Add(Const(1), Pow(PatternVar("u"), Const(2))))), 
        (Differentiate(ArcCot(PatternVar("u")), Var(var)), # NEW
            Neg(Div(Differentiate(PatternVar("u"), Var(var)),
                Add(Const(1), Pow(PatternVar("u"), Const(2)))))), # -u' / (1+u^2)
        (Differentiate(ArcSec(PatternVar("u")), Var(var)), # NEW
            Div(Differentiate(PatternVar("u"), Var(var)),
                Mul(Abs(PatternVar("u")), Pow(Sub(Pow(PatternVar("u"), Const(2)), Const(1)), Div(Const(1), Const(2)))))), # u' / (|u| * sqrt(u^2-1))
        (Differentiate(ArcCsc(PatternVar("u")), Var(var)), # NEW
            Neg(Div(Differentiate(PatternVar("u"), Var(var)),
                Mul(Abs(PatternVar("u")), Pow(Sub(Pow(PatternVar("u"), Const(2)), Const(1)), Div(Const(1), Const(2))))))), # -u' / (|u| * sqrt(u^2-1))


        # ----- Hyperbolic Functions (NEW) -----
        (Differentiate(Sinh(PatternVar("u")), Var(var)),
            Mul(Cosh(PatternVar("u")), Differentiate(PatternVar("u"), Var(var)))),
        (Differentiate(Cosh(PatternVar("u")), Var(var)),
            Mul(Sinh(PatternVar("u")), Differentiate(PatternVar("u"), Var(var)))),
        (Differentiate(Tanh(PatternVar("u")), Var(var)),
            Mul(Pow(Sech(PatternVar("u")), Const(2)), Differentiate(PatternVar("u"), Var(var)))),
        (Differentiate(Coth(PatternVar("u")), Var(var)),
            Neg(Mul(Pow(Csch(PatternVar("u")), Const(2)), Differentiate(PatternVar("u"), Var(var))))),
        (Differentiate(Sech(PatternVar("u")), Var(var)),
            Neg(Mul(Mul(Sech(PatternVar("u")), Tanh(PatternVar("u"))), Differentiate(PatternVar("u"), Var(var))))),
        (Differentiate(Csch(PatternVar("u")), Var(var)),
            Neg(Mul(Mul(Csch(PatternVar("u")), Coth(PatternVar("u"))), Differentiate(PatternVar("u"), Var(var))))),
        

        # ----- Unary negation -----
        (Differentiate(Neg(PatternVar("u")), Var(var)),
        Neg(Differentiate(PatternVar("u"), Var(var)))),
    ]
    
    result = Differentiate(expr, v)
    prev = None
    while prev != repr(result):
        prev = repr(result)
        result = rewrite(result, diff_rules)
        result = rewrite(result, simplification_rules())
    return result