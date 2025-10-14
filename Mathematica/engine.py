# engine.py
# (Pattern Matching, Substitution, Rewrite Engine, and Constant Folding implementation)

from typing import Any, Dict, List, Tuple, Optional
from logger import log_step 

# Import all needed Expression classes and PatternVar from rules.py for type hints and implementation
from rules import (
    Expr, Const, Var, PatternVar, Add, Mul, Sub, Div, Pow, 
    # Add other classes needed for 'evaluate_constants' and function bodies
) 

# ============================================================
# Pattern Matching / Substitution
# ============================================================

def match(pattern: Expr, expr: Expr, bindings: Optional[Dict[str, Expr]] = None) -> Optional[Dict[str, Expr]]:
    if bindings is None: bindings = {}
    if isinstance(pattern, PatternVar):
        if pattern.name in bindings:
            return bindings if bindings[pattern.name] == expr else None
        bindings[pattern.name] = expr
        return bindings
    if type(pattern) is not type(expr): return None
    if isinstance(pattern, Const):
        pv = pattern.value
        if isinstance(pv, PatternVar):
            if pv.name in bindings:
                return bindings if bindings[pv.name] == expr else None
            bindings[pv.name] = expr
            return bindings
        return bindings if pattern.value == expr.value else None
    if isinstance(pattern, Var):
        pn = pattern.name
        if isinstance(pn, PatternVar):
            if pn.name in bindings:
                return bindings if bindings[pn.name] == expr else None
            bindings[pn.name] = expr
            return bindings
        return bindings if pattern.name == expr.name else None
    for p_child, e_child in zip(pattern.children(), expr.children()):
        bindings = match(p_child, e_child, bindings)
        if bindings is None: return None
    return bindings

def substitute(expr: Expr, bindings: Dict[str, Expr]) -> Expr:
    if isinstance(expr, PatternVar): return bindings.get(expr.name, expr)
    if isinstance(expr, Const):
        v = expr.value
        if isinstance(v, PatternVar): return bindings.get(v.name, expr)
        return expr
    if isinstance(expr, Var):
        n = expr.name
        if isinstance(n, PatternVar): return bindings.get(n.name, expr)
        return expr
    args = [substitute(child, bindings) for child in expr.children()]
    return type(expr)(*args)

# ============================================================
# Rewrite Engine with Logging
# ============================================================

def rewrite(expr: Expr, rules: List[Tuple[Expr, Expr]]) -> Expr:
    changed = True
    while changed:
        changed, expr = _rewrite_once(expr, rules)
        expr = evaluate_constants(expr)
    return expr

def _rewrite_once(expr: Expr, rules: List[Tuple[Expr, Expr]]) -> Tuple[bool, Expr]:
    for pattern, replacement in rules:
        bindings = match(pattern, expr)
        if bindings is not None:
            new_expr = substitute(replacement, bindings)
            log_step(f"{pattern} -> {replacement} on {expr}")
            return True, new_expr
            
    fields = getattr(expr, "__dataclass_fields__", {})
    field_names = list(fields.keys())

    for field in field_names: # 'field' is the name string, e.g. "left"
        val = getattr(expr, field)
        if isinstance(val, Expr):
            changed, new_val = _rewrite_once(val, rules)
            if changed:
                # Create a new instance with the rewritten child
                new_args = [getattr(expr, name) for name in field_names]
                # 'field' is the name of the attribute that was changed, so we find its index
                new_args[field_names.index(field)] = new_val
                
                return True, type(expr)(*new_args)
    return False, expr

# ============================================================
# Constant Folding
# ============================================================

def evaluate_constants(expr: Expr) -> Expr:
    if isinstance(expr, Add):
        left, right = evaluate_constants(expr.left), evaluate_constants(expr.right)
        if isinstance(left, Const) and isinstance(right, Const): return Const(left.value + right.value)
        return Add(left, right)
    if isinstance(expr, Mul):
        left, right = evaluate_constants(expr.left), evaluate_constants(expr.right)
        if isinstance(left, Const) and isinstance(right, Const): return Const(left.value * right.value)
        return Mul(left, right)
    if isinstance(expr, Sub):
        left, right = evaluate_constants(expr.left), evaluate_constants(expr.right)
        if isinstance(left, Const) and isinstance(right, Const): return Const(left.value - right.value)
        return Sub(left, right)
    if isinstance(expr, Div):
        left, right = evaluate_constants(expr.left), evaluate_constants(expr.right)
        if isinstance(left, Const) and isinstance(right, Const): return Const(left.value / right.value)
        return Div(left, right)
    if isinstance(expr, Pow):
        base, exp = evaluate_constants(expr.base), evaluate_constants(expr.exp)
        if isinstance(base, Const) and isinstance(exp, Const):
            # --- handle edge cases ---
            if base.value == 0 and exp.value == 0:
                return Const(1)  # define 0^0 = 1 symbolically
            if base.value == 0 and exp.value < 0:
                return Const(float("inf"))  # symbolic infinity
            return Const(base.value ** exp.value)
        return Pow(base, exp)
    # Recursively apply constant folding to unary functions
    if hasattr(expr, 'arg'):
        new_arg = evaluate_constants(expr.arg)
        if new_arg != expr.arg:
            return type(expr)(new_arg)
    return expr