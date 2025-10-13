# ============================================================
# Differentiation
# ============================================================
from rules import *
from simplification import *
def differentiate(expr: Expr, var: str) -> Expr:
    reset_log()
    v = Var(var)
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

        # --- IMPORTANT FIX: Constant Power Rule (u^n) must be FIRST (more specific) ---
        (Differentiate(Pow(PatternVar("u"), Const(PatternVar("n"))), Var(var)),
            Mul(Const(PatternVar("n")),
                Mul(Pow(PatternVar("u"), Sub(Const(PatternVar("n")), Const(1))),
                    Differentiate(PatternVar("u"), Var(var))))),
        
        # --- General Power Rule (u^w, must be SECOND / more general) ---
        # d/dx(u^w) = u^w * [ w' * ln(u) + w * (u'/u) ]
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

        # ----- Inverse Trig -----
        (Differentiate(ArcSin(PatternVar("u")), Var(var)),
            Div(Differentiate(PatternVar("u"), Var(var)),
                Pow(Sub(Const(1), Pow(PatternVar("u"), Const(2))),
                    Div(Const(1), Const(2))))), # 1 / (1-u^2)^0.5 * u'
        
        (Differentiate(ArcCos(PatternVar("u")), Var(var)),
            Neg(Div(Differentiate(PatternVar("u"), Var(var)),
                Pow(Sub(Const(1), Pow(PatternVar("u"), Const(2))),
                    Div(Const(1), Const(2)))))), # -1 / (1-u^2)^0.5 * u'

        (Differentiate(ArcTan(PatternVar("u")), Var(var)),
            Div(Differentiate(PatternVar("u"), Var(var)),
                Add(Const(1), Pow(PatternVar("u"), Const(2))))), # 1 / (1+u^2) * u'


        # ----- Unary negation -----
        (Differentiate(Neg(PatternVar("u")), Var(var)),
        Neg(Differentiate(PatternVar("u"), Var(var)))),

        # ----- Reciprocal trigonometric functions -----
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
    ]
    
    result = Differentiate(expr, v)
    prev = None
    while prev != repr(result):
        prev = repr(result)
        result = rewrite(result, diff_rules)
        result = rewrite(result, simplification_rules())
    return result