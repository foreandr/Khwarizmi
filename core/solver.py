# core/solver.py
# ------------------------------------------------------------
# Simplification Strategy Layer
# ------------------------------------------------------------

from .expr import Expr
from .rules import list_rules, get_rule
from .proof_kernel import ProofKernel
from typing import Callable, Tuple

def simplify(expr: Expr, kernel: ProofKernel) -> Tuple[Expr, bool]:
    """
    Applies all available rewrite rules iteratively until the expression 
    is fully simplified (no rules can be applied further).
    
    This implements a basic saturation strategy.
    
    Returns the simplified expression and a boolean indicating if any changes were made.
    """
    
    rule_names = list_rules()
    rules = [(get_rule(name).name, get_rule(name).apply, get_rule(name).description) for name in rule_names]
    
    current_expr = expr
    changed = True
    iteration = 0
    
    # Keep iterating as long as we make progress
    while changed:
        iteration += 1
        changed = False
        print(f"\n--- SIMPLIFY ITERATION {iteration}: {current_expr} ---") # DEBUG: Starting expression for the cycle
        
        # Try every single rule on the current expression
        for rule_name, rule_fn, rule_desc in rules:
            
            # Apply rule through the kernel; the kernel handles recursion (deep application)
            new_expr = kernel.apply_rule(
                current_expr, 
                rule_fn, 
                rule_name, 
                rule_desc
            )
            
            # Check if the kernel actually changed the expression
            if str(new_expr) != str(current_expr):
                print(f"  [APPLIED] {rule_name}: {current_expr} -> {new_expr}") # DEBUG: Successful rule application
                current_expr = new_expr
                changed = True
                # If a change occurred, restart the entire rule application loop 
                break 
                
    return current_expr, str(current_expr) != str(expr)