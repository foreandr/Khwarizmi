# ============================================================
# equality.py — Expression Equivalence Checking
# ============================================================

from rules import *  # imports Expr, Add, Mul, rewrite, simplification_rules, evaluate_constants

def check_equal(expr1: Expr, expr2: Expr) -> bool:
    """
    Determine if two expressions are mathematically equivalent
    by applying the rewrite engine and simplification rules.
    Handles associativity for Add and Mul.
    """

    # --------------------------------------------------------
    # Simplify expression repeatedly until stable
    # --------------------------------------------------------
    def simplify(expr: Expr) -> Expr:
        prev = None
        while prev != repr(expr):
            prev = repr(expr)
            expr = rewrite(expr, simplification_rules())
            expr = evaluate_constants(expr)
        return expr

    # --------------------------------------------------------
    # Flatten associative operations (Add, Mul)
    # --------------------------------------------------------
    def flatten_add(expr):
        if isinstance(expr, Add):
            return flatten_add(expr.left) + flatten_add(expr.right)
        return [expr]

    def flatten_mul(expr):
        if isinstance(expr, Mul):
            return flatten_mul(expr.left) + flatten_mul(expr.right)
        return [expr]

    # --------------------------------------------------------
    # Canonicalize structure (order-insensitive for Add/Mul)
    # --------------------------------------------------------
    def canonicalize(expr: Expr) -> Expr:
        if isinstance(expr, Add):
            terms = sorted([repr(t) for t in flatten_add(expr)])
            return terms  # return canonical list representation
        if isinstance(expr, Mul):
            factors = sorted([repr(f) for f in flatten_mul(expr)])
            return factors
        if isinstance(expr, Sub):
            return Sub(canonicalize(expr.left), canonicalize(expr.right))
        if isinstance(expr, Div):
            return Div(canonicalize(expr.left), canonicalize(expr.right))
        if isinstance(expr, Pow):
            return Pow(canonicalize(expr.base), canonicalize(expr.exp))
        if isinstance(expr, Exp):
            return Exp(canonicalize(expr.arg))
        if isinstance(expr, Log):
            return Log(canonicalize(expr.arg))
        if isinstance(expr, Sin):
            return Sin(canonicalize(expr.arg))
        if isinstance(expr, Cos):
            return Cos(canonicalize(expr.arg))
        if isinstance(expr, Tan):
            return Tan(canonicalize(expr.arg))
        return expr

    # --------------------------------------------------------
    # Comparison logic
    # --------------------------------------------------------
    e1 = canonicalize(simplify(expr1))
    e2 = canonicalize(simplify(expr2))

    def equivalent(a, b):
        # If flattened lists (Add/Mul terms), compare as sets
        if isinstance(a, list) and isinstance(b, list):
            return sorted(a) == sorted(b)
        return repr(a) == repr(b)

    return equivalent(e1, e2)
