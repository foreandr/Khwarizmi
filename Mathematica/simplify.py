from .expr import *
from .pattern import PatternVar

def simplification_rules():
    return [
        (Add(PatternVar("x"), Const(0)), PatternVar("x")),
        (Add(Const(0), PatternVar("x")), PatternVar("x")),
        (Sub(PatternVar("x"), Const(0)), PatternVar("x")),
        (Mul(PatternVar("x"), Const(1)), PatternVar("x")),
        (Mul(Const(1), PatternVar("x")), PatternVar("x")),
        (Mul(PatternVar("x"), Const(0)), Const(0)),
        (Mul(Const(0), PatternVar("x")), Const(0)),
        (Pow(PatternVar("x"), Const(1)), PatternVar("x")),
        (Pow(PatternVar("x"), Const(0)), Const(1)),
        (Div(PatternVar("x"), Const(1)), PatternVar("x")),
    ]
