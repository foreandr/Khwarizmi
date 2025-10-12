from .expr import *
from .pattern import PatternVar
from .rewrite import rewrite
from .simplify import simplification_rules
from .logger import reset_log

def differentiate(expr, var: str):
    reset_log()
    v = Var(var)
    diff_rules = [
        (Differentiate(Const(PatternVar("c")), Var(PatternVar("vv"))), Const(0)),
        (Differentiate(Var(var), Var(var)), Const(1)),
        (Differentiate(Var(PatternVar("x")), Var(var)), Const(0)),

        # linear
        (Differentiate(Add(PatternVar("u"), PatternVar("w")), Var(var)),
            Add(Differentiate(PatternVar("u"), Var(var)), Differentiate(PatternVar("w"), Var(var)))),
        (Differentiate(Sub(PatternVar("u"), PatternVar("w")), Var(var)),
            Sub(Differentiate(PatternVar("u"), Var(var)), Differentiate(PatternVar("w"), Var(var)))),

        # product / quotient
        (Differentiate(Mul(PatternVar("u"), PatternVar("w")), Var(var)),
            Add(Mul(Differentiate(PatternVar("u"), Var(var)), PatternVar("w")),
                Mul(PatternVar("u"), Differentiate(PatternVar("w"), Var(var))))),
        (Differentiate(Div(PatternVar("u"), PatternVar("w")), Var(var)),
            Div(Sub(Mul(Differentiate(PatternVar("u"), Var(var)), PatternVar("w")),
                    Mul(PatternVar("u"), Differentiate(PatternVar("w"), Var(var)))),
                Pow(PatternVar("w"), Const(2)))),

        # power rule
        (Differentiate(Pow(PatternVar("u"), Const(PatternVar("n"))), Var(var)),
            Mul(Const(PatternVar("n")),
                Mul(Pow(PatternVar("u"), Sub(Const(PatternVar("n")), Const(1))),
                    Differentiate(PatternVar("u"), Var(var))))),

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
    ]

    result = Differentiate(expr, v)
    prev = None
    while prev != repr(result):
        prev = repr(result)
        result = rewrite(result, diff_rules)
        result = rewrite(result, simplification_rules())
    return result
