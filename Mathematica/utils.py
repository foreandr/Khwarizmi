# utils.py

from rules import Expr, Var, Const, Add, Mul, Div, Pow, Log, Exp, Sin, Cos, Tan, Neg, Sub, Abs, Integrate # Sub is imported!

def is_independent_of(expr: Expr, var: Var) -> bool:
    """Returns True if the expression does NOT contain the variable 'var'."""
    # Base Case 1: The variable is found.
    if isinstance(expr, Var) and expr.name == var.name:
        return False
    
    # Base Case 2: Terminal node (Const, Var that is not 'var')
    if isinstance(expr, (Const, Var)):
        return True
    
    # Base Case 3: Check Integral variables (if used)
    if isinstance(expr, Integrate) and expr.var.name == var.name:
        return False

    # Recursive Case: Check all children.
    # This assumes all expression classes in rules.py have a working children() method.
    for child in expr.children():
        if not is_independent_of(child, var):
            return False
            
    return True # If the loop finishes without finding 'var', it's independent.