from rules import (
    Var, Const, Add, Sub, Mul, Div, Pow,
    Exp, Log, Sin, Cos, Tan, Neg, Sec, Csc, Cot,
    ArcSin, ArcCos, ArcTan, ArcCsc, ArcSec, ArcCot,
    Sinh, Cosh, Tanh, Coth, Sech, Csch,
    Integrate
)

x = Var("x")

# ============================================================
# DIFFERENTIATION TESTS
# ============================================================

DIFFERENTIATION_TESTS = [
    # --- Polynomial ---
    {
        "name": "Polynomial Derivative (3x^2)",
        "expr": Mul(Const(3), Pow(x, Const(2))),
        "expected": Mul(Const(3), Mul(Const(2), x)),
    },
    {
        "name": "Polynomial Derivative (x^4)",
        "expr": Pow(x, Const(4)),
        "expected": Mul(Const(4), Pow(x, Const(3))),
    },

    # --- Exponential/Logarithmic ---
    {
        "name": "Exponential Derivative (e^2x)",
        "expr": Exp(Mul(Const(2), x)),
        "expected": Mul(Exp(Mul(Const(2), x)), Const(2)),
    },
    {
        "name": "Logarithmic Derivative (ln(x))",
        "expr": Log(x),
        "expected": Div(Const(1), x),
    },

    # --- Trigonometric ---
    {
        "name": "Trig Derivative (sin(x))",
        "expr": Sin(x),
        "expected": Cos(x),
    },
    {
        "name": "Trig Derivative (sec(x))",
        "expr": Sec(x),
        "expected": Mul(Sec(x), Tan(x)),
    },

    # --- Inverse Trigonometric ---
    {
        "name": "Inverse Trig Derivative (arcsin)",
        "expr": ArcSin(x),
        "expected": Div(Const(1), Pow(Sub(Const(1), Pow(x, Const(2))), Div(Const(1), Const(2)))),
    },
    {
        "name": "Inverse Trig Derivative (arccos)",
        "expr": ArcCos(x),
        "expected": Neg(Div(Const(1), Pow(Sub(Const(1), Pow(x, Const(2))), Div(Const(1), Const(2))))),
    },
    {
        "name": "Inverse Trig Derivative (arctan)",
        "expr": ArcTan(x),
        "expected": Div(Const(1), Add(Const(1), Pow(x, Const(2)))),
    },
    {
        "name": "Inverse Trig Derivative (arccot)",
        "expr": ArcCot(x),
        "expected": Neg(Div(Const(1), Add(Const(1), Pow(x, Const(2))))),
    },

    # --- Hyperbolic ---
    {
        "name": "Hyperbolic Derivative (sinh(x))",
        "expr": Sinh(x),
        "expected": Cosh(x),
    },
    {
        "name": "Hyperbolic Derivative (tanh(x))",
        "expr": Tanh(x),
        "expected": Pow(Sech(x), Const(2)),
    },

    # --- General Power / Composite ---
    {
        "name": "General Power Rule (x^x) Simplified",
        "expr": Pow(x, x),
        "expected": Mul(Pow(x, x), Add(Log(x), Const(1))),
    },
    {
        "name": "Full Composite Expression",
        "expr": Add(
            Add(Mul(Const(3), Pow(x, Const(2))), Const(4)),
            Add(
                Exp(Mul(Const(2), x)),
                Add(
                    Log(x),
                    Add(Sin(x), Add(Cos(x), Tan(x)))
                )
            )
        ),
        "expected": Add(
            Add(Mul(Const(3), Mul(Const(2), x)), Const(0)),
            Add(
                Mul(Exp(Mul(Const(2), x)), Const(2)),
                Add(
                    Div(Const(1), x),
                    Add(
                        Add(Cos(x), Mul(Const(-1), Sin(x))),
                        Div(Const(1), Pow(Cos(x), Const(2)))
                    )
                )
            )
        ),
    },

    # --- Negation / Reciprocal ---
    {
        "name": "Negation Derivative",
        "expr": Neg(Neg(x)),
        "expected": Const(1),
    },
    {
        "name": "Reciprocal Trig Derivative (sec)",
        "expr": Div(Const(1), Cos(x)),
        "expected": Mul(Div(Const(1), Cos(x)), Tan(x)),
    },
]

# ============================================================
# INTEGRATION TESTS
# ============================================================

INTEGRATION_TESTS = [
    {
        "name": "Integration Test (Power Rule x^3)",
        "expr": Pow(x, Const(3)),
        "expected": Div(Pow(x, Const(4)), Const(4)),
        "integrate_only": True,
    },
    {
        "name": "Integration Test (Linearity 2cos(x))",
        "expr": Mul(Const(2), Cos(x)),
        "expected": Mul(Const(2), Sin(x)),
        "integrate_only": True,
    },
    {
        "name": "Integration Test (sec^2(x))",
        "expr": Pow(Sec(x), Const(2)),
        "expected": Tan(x),
        "integrate_only": True,
    },
    {
        "name": "Integration Test (csc^2(x))",
        "expr": Pow(Csc(x), Const(2)),
        "expected": Neg(Cot(x)),
        "integrate_only": True,
    },
    {
        "name": "Integration Test (1/sqrt(1-x^2))",
        "expr": Div(Const(1), Pow(Sub(Const(1), Pow(x, Const(2))), Div(Const(1), Const(2)))),
        "expected": ArcSin(x),
        "integrate_only": True,
    },
    {
        "name": "Integration Test (1/(1+x^2))",
        "expr": Div(Const(1), Add(Const(1), Pow(x, Const(2)))),
        "expected": ArcTan(x),
        "integrate_only": True,
    },
    {
        "name": "Integration Test (U-Sub: Power Rule)",
        "expr": Mul(Pow(Add(Pow(x, Const(2)), Const(1)), Const(3)), Mul(Const(2), x)),
        "expected": Div(Pow(Add(Pow(x, Const(2)), Const(1)), Const(4)), Const(4)),
        "integrate_only": True,
    },
    {
        "name": "Integration Test (U-Sub: Cosine)",
        "expr": Mul(Cos(Pow(x, Const(2))), Mul(Const(2), x)),
        "expected": Sin(Pow(x, Const(2))),
        "integrate_only": True,
    },
    {
        "name": "Integration Test (U-Sub: Exponential)",
        "expr": Mul(Exp(Sin(x)), Cos(x)),
        "expected": Exp(Sin(x)),
        "integrate_only": True,
    },
    {
        "name": "Integration Test (Log Rule: 1/x)",
        "expr": Div(Const(1), x),
        "expected": Log(x),
        "integrate_only": True,
    },
    {
        "name": "Integration Test (Log Rule: 2x/(x^2+1))",
        "expr": Div(Mul(Const(2), x), Add(Pow(x, Const(2)), Const(1))),
        "expected": Log(Add(Pow(x, Const(2)), Const(1))),
        "integrate_only": True,
    },
    {
        "name": "Integration Test (IBP: x*e^x)",
        "expr": Mul(x, Exp(x)),
        "expected": Sub(Mul(x, Exp(x)), Exp(x)),
        "integrate_only": True,
    },
]

# ============================================================
# FINAL TESTS OBJECT
# ============================================================

TESTS = DIFFERENTIATION_TESTS + INTEGRATION_TESTS
