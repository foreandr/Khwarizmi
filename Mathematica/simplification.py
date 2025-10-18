from rules import *
import math

# ============================================================
# Simplification Rules
# ============================================================
def simplification_rules() -> List[Tuple[Expr, Expr]]:
    return [
        # ---------- Algebraic base identities ----------
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

        # --- NEW: General Algebraic Simplifications ---
        (Mul(PatternVar("x"), Div(Const(1), PatternVar("x"))), Const(1)),
        (Mul(Div(Const(1), PatternVar("x")), PatternVar("x")), Const(1)),
        (Pow(Pow(PatternVar("u"), PatternVar("n")), PatternVar("m")),
         Pow(PatternVar("u"), Mul(PatternVar("n"), PatternVar("m")))),

        # ---------- Negation simplifications ----------
        (Neg(Const(0)), Const(0)),
        (Neg(Const(-1)), Const(1)),
        (Neg(Const(1)), Const(-1)),
        (Neg(Neg(PatternVar("x"))), PatternVar("x")),
        (Mul(Const(-1), PatternVar("x")), Neg(PatternVar("x"))),
        (Mul(PatternVar("x"), Const(-1)), Neg(PatternVar("x"))),
        (Add(PatternVar("x"), Neg(PatternVar("x"))), Const(0)),
        (Sub(PatternVar("x"), PatternVar("x")), Const(0)),

        # ---------- Log/Exp identities ----------
        (Exp(Log(PatternVar("x"))), PatternVar("x")),
        (Log(Const(math.e)), Const(1)),
        (Log(Const(2.71828)), Const(1)),

        # ---------- Power/Reciprocal identities ----------
        (Div(Const(1), Pow(PatternVar("x"), PatternVar("n"))),
         Pow(PatternVar("x"), Neg(PatternVar("n")))),
        (Div(PatternVar("x"), PatternVar("x")), Const(1)),

        # ---------- Reciprocal trig identities ----------
        (Sec(PatternVar("u")), Div(Const(1), Cos(PatternVar("u")))),
        (Csc(PatternVar("u")), Div(Const(1), Sin(PatternVar("u")))),
        (Cot(PatternVar("u")), Div(Cos(PatternVar("u")), Sin(PatternVar("u")))),

        # ---------- Canonical trig identities ----------
        (Add(Pow(Tan(PatternVar("u")), Const(2)), Const(1)),
         Div(Const(1), Pow(Cos(PatternVar("u")), Const(2)))),
        (Add(Const(1), Pow(Tan(PatternVar("u")), Const(2))),
         Div(Const(1), Pow(Cos(PatternVar("u")), Const(2)))),
        (Div(Const(1), Pow(Cos(PatternVar("u")), Const(2))),
         Pow(Sec(PatternVar("u")), Const(2))),

        (Sub(Const(0), PatternVar("x")), Mul(Const(-1), PatternVar("x"))),
        (Sub(Const(0), Mul(Const(-1), PatternVar("x"))), PatternVar("x")),
        (Add(Const(0), PatternVar("x")), PatternVar("x")),
        (Add(PatternVar("x"), Const(0)), PatternVar("x")),
        (Sub(PatternVar("x"), Const(0)), PatternVar("x")),
        (Div(Sin(PatternVar("u")), Cos(PatternVar("u"))), Tan(PatternVar("u"))),

        # ---------- Negation simplifications (advanced) ----------
        (Mul(Const(-1), Mul(Const(-1), PatternVar("x"))), PatternVar("x")),
        (Mul(Const(-1), Const(-1)), Const(1)),
        (Sub(Const(0), Sub(Const(0), PatternVar("x"))), PatternVar("x")),
        (Div(Sin(PatternVar("u")), Pow(Cos(PatternVar("u")), Const(2))),
         Mul(Div(Const(1), Cos(PatternVar("u"))), Tan(PatternVar("u")))),
        (Exp(Log(PatternVar("x"))), PatternVar("x")),
        (Log(Exp(PatternVar("x"))), PatternVar("x")),
        (Log(Const(math.e)), Const(1)),
        (Div(Const(1), Pow(PatternVar("x"), PatternVar("n"))),
         Pow(PatternVar("x"), Neg(PatternVar("n")))),
        (Pow(PatternVar("x"), Const(-1)), Div(Const(1), PatternVar("x"))),
        (Div(PatternVar("x"), PatternVar("x")), Const(1)),

        # ========================================================
        # >>> NEW RULES: Fix for linear integrating factor bug <<<
        # ========================================================
        # (-(y/x))/y  →  -1/x
        (Div(Neg(Div(PatternVar("y"), PatternVar("x"))), PatternVar("y")),
         Neg(Div(Const(1), PatternVar("x")))),

        # (-y/x)/y  →  -1/x  (alternate form)
        (Div(Div(Neg(PatternVar("y")), PatternVar("x")), PatternVar("y")),
         Neg(Div(Const(1), PatternVar("x")))),

        # (y/x)/y  →  1/x
        (Div(Div(PatternVar("y"), PatternVar("x")), PatternVar("y")),
         Div(Const(1), PatternVar("x"))),

        # ((y/x)*(-1))/y  →  -1/x  (just in case Neg collapsed differently)
        (Div(Mul(Div(PatternVar("y"), PatternVar("x")), Const(-1)), PatternVar("y")),
         Neg(Div(Const(1), PatternVar("x")))),
    ]
