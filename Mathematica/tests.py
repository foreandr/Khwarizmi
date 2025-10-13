from rules import (
    Var, Const, Add, Sub, Mul, Div, Pow,
    Exp, Log, Sin, Cos, Tan, Neg, Sec, ArcSin, # Added ArcSin
)

x = Var("x")

TESTS = [
    # --- Polynomial ---
    {
        "name": "Polynomial Derivative",
        "expr": Mul(Const(3), Pow(x, Const(2))),
        "expected": Mul(Const(3), Mul(Const(2), x)),  # 3*(2*x)
    },

    # --- Exponential ---
    {
        "name": "Exponential Derivative",
        "expr": Exp(Mul(Const(2), x)),
        "expected": Mul(Exp(Mul(Const(2), x)), Const(2)),
    },

    # --- Logarithmic ---
    {
        "name": "Logarithmic Derivative",
        "expr": Log(x),
        "expected": Div(Const(1), x),
    },

    # --- Trigonometric ---
    {
        "name": "Trigonometric Derivative (sin)",
        "expr": Sin(x),
        "expected": Cos(x),
    },
    {
        "name": "Trigonometric Derivative (cos)",
        "expr": Cos(x),
        "expected": Mul(Const(-1), Sin(x)),
    },
    {
        "name": "Trigonometric Derivative (tan)",
        "expr": Tan(x),
        "expected": Div(Const(1), Pow(Cos(x), Const(2))),  # canonical cosine form
    },
    
    # --- NEW: Inverse Trigonometric ---
    {
        "name": "Inverse Trig Derivative (arcsin)",
        "expr": ArcSin(x),
        "expected": Div(Const(1), Pow(Sub(Const(1), Pow(x, Const(2))), Div(Const(1), Const(2)))), # 1 / (1-x^2)^0.5
    },

    # --- Composite Expression ---
    {
        "name": "Full Composite Expression",
        "expr": Add(
            Add(Mul(Const(3), Pow(x, Const(2))), Const(4)),
            Add(
                Exp(Mul(Const(2), x)),
                Add(
                    Log(x),
                    Add(
                        Sin(x),
                        Add(Cos(x), Tan(x))
                    )
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

    # --- Negation Simplification (symbolic only) ---
    {
        "name": "Negation Simplification",
        "expr": Neg(Neg(x)),
        "expected": x,
        "simplify_only": True,
    },

    # --- Negation Derivative ---
    {
        "name": "Negation Derivative",
        "expr": Neg(Neg(x)),
        "expected": Const(1),
    },

    # --- Reciprocal Trig Simplification (sec) ---
    {
        "name": "Reciprocal Trig Simplification (sec)",
        "expr": Div(Const(1), Cos(x)),
        "expected": Div(Const(1), Cos(x)),
        "simplify_only": True,
    },

    # --- Reciprocal Trig Derivative (sec) ---
    {
        "name": "Reciprocal Trig Derivative (sec)",
        "expr": Div(Const(1), Cos(x)),
        "expected": Mul(Div(Const(1), Cos(x)), Tan(x)),  # (1/cos(x)) * tan(x)
    },
]