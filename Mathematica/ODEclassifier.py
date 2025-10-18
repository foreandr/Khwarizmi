# ODEclassifier.py

from rules import Expr, Var, Const, Add, Mul, Div, Pow, Log, Exp, Sin, Cos, Neg, Sub # Sub is imported!
from utils import is_independent_of
from typing import Literal

def classify_first_order(f_xy: Expr, x_var: str = "x", y_var: str = "y") -> Literal["Separable-f(x)", "Separable-f(y)", "Separable-g(x)h(y)", "Linear", "Homogeneous", "General"]:
    """
    Classifies a first-order ODE given in the explicit form dy/dx = f(x, y).
    """
    
    x = Var(x_var)
    y = Var(y_var)
    
    # --------------------------------------------------
    # 1. Separable Check: f(x, y) = g(x) * h(y)
    # --------------------------------------------------

    # Check 1.1: Trivial Separable: f(x,y) contains only x or only y terms.
    f_is_g_x = is_independent_of(f_xy, y)
    f_is_h_y = is_independent_of(f_xy, x)
    
    if f_is_g_x:
        return "Separable-f(x)"
    
    if f_is_h_y:
        return "Separable-f(y)"

    # Check 1.2: Multiplicative Separable (g(x) * h(y))
    if isinstance(f_xy, (Mul, Div)) and not f_is_g_x and not f_is_h_y:
        return "Separable-g(x)h(y)"
        
    # --------------------------------------------------
    # 2. Fallback
    # --------------------------------------------------
    
    return "General"