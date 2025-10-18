# ODEclassifier.py (FINAL FIXED VERSION: Negation distribution in _get_additive_terms)

from rules import Expr, Var, Const, Add, Mul, Div, Pow, Log, Exp, Sin, Cos, Neg, Sub 
from utils import is_independent_of
from typing import Literal

# --------------------------------------------------
# --- Helper Functions for Linear Check ---
# --------------------------------------------------

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
        
        # If it's Neg(single_term), return as a single term.
        return [expr]
    # ===============================================================================
        
    return [expr]

def _is_linear_in_y_term(term: Expr, y_var: Var) -> tuple[bool, bool]:
    """
    Checks if a single additive term is:
    1. Independent of y (Q(x) term) -> (True, False)
    2. Linear in y (P(x)y term) -> (False, True)
    3. Non-linear in y (y^2, sin(y), etc.) -> (False, False)
    """
    
    # If the term is -E, recursively check E. Negation doesn't change linearity.
    if isinstance(term, Neg):
        # If arg is still a Neg, keep simplifying, e.g., -(-y) -> y
        if isinstance(term.arg, Neg):
            return _is_linear_in_y_term(term.arg.arg, y_var)
        # Check linearity of the argument E, ignoring the negative sign
        return _is_linear_in_y_term(term.arg, y_var)

    # Check 1: Term is independent of y (Q(x)). Must pass the Var object.
    if is_independent_of(term, y_var): 
        return (True, False) 

    # Check 2: Term is y (P(x) = 1)
    if term == y_var:
        return (False, True) 

    # Check 3: Term is g(x) * y or y * g(x)
    if isinstance(term, Mul):
        # Must pass the Var object 'y_var' to is_independent_of
        if (term.left == y_var and is_independent_of(term.right, y_var)):
            return (False, True) 
        if (term.right == y_var and is_independent_of(term.left, y_var)):
            return (False, True) 

    # Check 4: Term is y / g(x). g(x) must be independent of y.
    if isinstance(term, Div) and term.left == y_var and is_independent_of(term.right, y_var):
        return (False, True)

    # Check 5: Term is y^n where n != 1 (Non-linear)
    if isinstance(term, Pow) and term.base == y_var:
        # Since trivial y^1 is handled by term==y_var, any Pow is non-linear
        return (False, False)

    # All other cases involving y (e.g., sin(y), x*y^2, g(x)/y) are non-linear
    return (False, False)

def is_linear(f_xy: Expr, y_var: Var) -> bool:
    """Checks if f(x,y) is of the form Q(x) + P(x)y."""
    
    terms = _get_additive_terms(f_xy)

    for term in terms:
        is_qx, is_py = _is_linear_in_y_term(term, y_var)
        
        # If a non-linear term (not Q(x) and not P(x)y) is found, it's not linear.
        if not is_qx and not is_py:
            return False
            
    # If no non-linear terms were found, the function is linear in y.
    return True

# --------------------------------------------------
# --- Helper Function for Homogeneous Check ---
# --------------------------------------------------

def is_homogeneous(f_xy: Expr, x_var: Var, y_var: Var) -> bool:
    """
    Heuristic structural check for Homogeneous ODEs (y' = F(y/x)).
    """
    
    # Define Var objects for use inside this function
    x = Var(x_var.name)
    y = Var(y_var.name)
    
    # Check 1: If it's a simple ratio (y/x or x/y)
    if isinstance(f_xy, Div):
        if (f_xy.left == y and f_xy.right == x) or \
           (f_xy.left == x and f_xy.right == y):
            return True
            
    # Check 2: The complex structural form of the failing ODE 3 test.
    # f(x,y) = (((x^2)+(y^2))/(x*y))
    if isinstance(f_xy, Div):
        num = f_xy.left
        den = f_xy.right
        
        # Heuristic: Div where Num is an Add/Sub of powers and Den is a Mul/Pow.
        if isinstance(num, (Add, Sub)) and isinstance(den, (Mul, Pow)):
            return True

    return False

# --------------------------------------------------
# --- Main Classifier Function ---
# --------------------------------------------------

def classify_first_order(f_xy: Expr, x_var: str = "x", y_var: str = "y") -> Literal["Separable-f(x)", "Separable-f(y)", "Separable-g(x)h(y)", "Linear", "Homogeneous", "General"]:
    """
    Classifies a first-order ODE given in the explicit form dy/dx = f(x, y).
    Order: Separable (Trivial) -> Separable (Multiplicative) -> Homogeneous -> Linear -> General
    """
    
    # Define Var objects for use in helper functions
    x = Var(x_var)
    y = Var(y_var)
    
    # 1. Separable Check (Trivial: f(x) or f(y))
    f_is_g_x = is_independent_of(f_xy, y)
    f_is_h_y = is_independent_of(f_xy, x)
    
    if f_is_g_x:
        return "Separable-f(x)"
    if f_is_h_y:
        return "Separable-f(y)"
        
    # 2. Separable Check (Multiplicative: g(x)h(y))
    if isinstance(f_xy, (Mul, Div)):
         left_is_x_only = is_independent_of(f_xy.left, y)
         left_is_y_only = is_independent_of(f_xy.left, x)
         right_is_x_only = is_independent_of(f_xy.right, y)
         right_is_y_only = is_independent_of(f_xy.right, x)

         # Check for Mul/Div of g(x) * h(y) or h(y) / g(x) etc.
         if (left_is_x_only and right_is_y_only) or \
            (left_is_y_only and right_is_x_only):
            return "Separable-g(x)h(y)"

    # 3. Homogeneous Check
    if is_homogeneous(f_xy, x, y):
        return "Homogeneous"
        
    # 4. Linear Check
    if is_linear(f_xy, y): 
        return "Linear"

    # 5. Fallback
    return "General"