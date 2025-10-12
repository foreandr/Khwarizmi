from dataclasses import dataclass
from .expr import *

@dataclass
class PatternVar(Expr):
    name: str
    def __repr__(self):
        return f"?{self.name}"

def match(pattern: Expr, expr: Expr, bindings=None):
    if bindings is None:
        bindings = {}

    if isinstance(pattern, PatternVar):
        if pattern.name in bindings:
            return bindings if bindings[pattern.name] == expr else None
        bindings[pattern.name] = expr
        return bindings

    if type(pattern) is not type(expr):
        return None

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
        if bindings is None:
            return None

    return bindings

def substitute(expr: Expr, bindings: dict):
    if isinstance(expr, PatternVar):
        return bindings.get(expr.name, expr)
    if isinstance(expr, Const):
        v = expr.value
        if isinstance(v, PatternVar):
            return bindings.get(v.name, expr)
        return expr
    if isinstance(expr, Var):
        n = expr.name
        if isinstance(n, PatternVar):
            return bindings.get(n.name, expr)
        return expr
    args = [substitute(child, bindings) for child in expr.children()]
    return type(expr)(*args)
