# ============================================================
# ODEclassifier.py — fully fixed version
# ============================================================

from rules import Expr, Var, Const, Add, Mul, Div, Pow, Log, Exp, Sin, Cos, Neg, Sub
from utils import is_independent_of
from typing import Literal

# ------------------------------------------------------------
# --- Helper Functions for Linear Check ---
# ------------------------------------------------------------

def _get_additive_terms(expr):
    """
    Recursively flattens Add/Sub into a list of additive terms,
    and distributes a leading Negation of an Add/Sub.
    """
    if isinstance(expr, Add):
        return _get_additive_terms(expr.left) + _get_additive_terms(expr.right)

    if isinstance(expr, Sub):
        # a - b is a + (-b)
        return _get_additive_terms(expr.left) + [Neg(expr.right)]

    # === CRITICAL FIX: Distribute leading Negation to handle -(A+B) and -(A-B) ===
    if isinstance(expr, Neg):
        arg = expr.arg
        if isinstance(arg, Add):
            # -(A+B) = (-A) + (-B)
            return _get_additive_terms(Neg(arg.left)) + _get_additive_terms(Neg(arg.right))
        if isinstance(arg, Sub):
            # -(A-B) = (-A) + B
            return _get_additive_terms(Neg(arg.left)) + _get_additive_terms(arg.right)
        # Simple -term
        return [expr]

    return [expr]


def _is_linear_in_y_term(term: Expr, y_var: Var) -> tuple[bool, bool]:
    """
    Checks if a single additive term is:
    1. Independent of y (Q(x) term) -> (True, False)
    2. Linear in y (P(x)y term) -> (False, True)
    3. Non-linear in y (y^2, sin(y), etc.) -> (False, False)
    """

    # Negations don't change linearity
    if isinstance(term, Neg):
        if isinstance(term.arg, Neg):
            return _is_linear_in_y_term(term.arg.arg, y_var)
        return _is_linear_in_y_term(term.arg, y_var)

    # 1. Independent of y
    if is_independent_of(term, y_var):
        return (True, False)

    # 2. Direct y
    if term == y_var:
        return (False, True)

    # 3. g(x)*y or y*g(x)
    if isinstance(term, Mul):
        if term.left == y_var and is_independent_of(term.right, y_var):
            return (False, True)
        if term.right == y_var and is_independent_of(term.left, y_var):
            return (False, True)

    # 4. y/g(x)
    if isinstance(term, Div) and term.left == y_var and is_independent_of(term.right, y_var):
        return (False, True)

    # 5. y^n with n != 1
    if isinstance(term, Pow) and term.base == y_var:
        return (False, False)

    # Anything else with y is nonlinear
    return (False, False)


def is_linear(f_xy: Expr, y_var: Var) -> bool:
    """Checks if f(x,y) is of the form Q(x) + P(x)y."""
    terms = _get_additive_terms(f_xy)
    for term in terms:
        is_qx, is_py = _is_linear_in_y_term(term, y_var)
        if not is_qx and not is_py:
            return False
    return True

# ------------------------------------------------------------
# --- Helper Function for Homogeneous Check ---
# ------------------------------------------------------------

def is_homogeneous(f_xy: Expr, x_var: Var | str, y_var: Var | str) -> bool:
    """
    Heuristic structural check for Homogeneous ODEs (y' = F(y/x)).
    """
    # Define Var objects correctly whether strings or Vars
    x = Var(x_var if isinstance(x_var, str) else x_var.name)
    y = Var(y_var if isinstance(y_var, str) else y_var.name)

    # Simple ratio check
    if isinstance(f_xy, Div):
        if (f_xy.left == y and f_xy.right == x) or (f_xy.left == x and f_xy.right == y):
            return True

    # Heuristic structural form
    if isinstance(f_xy, Div):
        num, den = f_xy.left, f_xy.right
        if isinstance(num, (Add, Sub)) and isinstance(den, (Mul, Pow)):
            return True

    return False

# ------------------------------------------------------------
# --- Main Classifier Function ---
# ------------------------------------------------------------

def classify_first_order(
    f_xy: Expr,
    x_var: str = "x",
    y_var: str = "y",
) -> Literal[
    "Separable-f(x)",
    "Separable-f(y)",
    "Separable-g(x)h(y)",
    "Linear",
    "Homogeneous",
    "General",
]:
    """
    Classifies a first-order ODE in explicit form dy/dx = f(x,y).
    Order: Separable (Trivial) -> Separable (Multiplicative) -> Homogeneous -> Linear -> General
    """

    x = Var(x_var)
    y = Var(y_var)

    # 1. Separable f(x) or f(y)
    f_is_g_x = is_independent_of(f_xy, y)
    f_is_h_y = is_independent_of(f_xy, x)
    if f_is_g_x:
        return "Separable-f(x)"
    if f_is_h_y:
        return "Separable-f(y)"

    # 2. Multiplicative g(x)h(y)
    if isinstance(f_xy, (Mul, Div)):
        left_is_x_only = is_independent_of(f_xy.left, y)
        left_is_y_only = is_independent_of(f_xy.left, x)
        right_is_x_only = is_independent_of(f_xy.right, y)
        right_is_y_only = is_independent_of(f_xy.right, x)
        if (left_is_x_only and right_is_y_only) or (left_is_y_only and right_is_x_only):
            return "Separable-g(x)h(y)"

    # 3. Homogeneous
    if is_homogeneous(f_xy, x, y):
        return "Homogeneous"

    # 4. Linear
    if is_linear(f_xy, y):
        return "Linear"

    # 5. Fallback
    return "General"
