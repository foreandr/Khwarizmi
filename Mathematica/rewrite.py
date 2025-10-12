from .expr import *
from .pattern import match, substitute
from .logger import log_step

def rewrite(expr, rules):
    changed = True
    while changed:
        changed, expr = _rewrite_once(expr, rules)
        expr = evaluate_constants(expr)
    return expr

def _rewrite_once(expr, rules):
    for pattern, replacement in rules:
        bindings = match(pattern, expr)
        if bindings is not None:
            new_expr = substitute(replacement, bindings)
            log_step(f"{pattern} -> {replacement} on {expr}")
            return True, new_expr

    for field in getattr(expr, "__dataclass_fields__", {}):
        val = getattr(expr, field)
        if isinstance(val, Expr):
            changed, new_val = _rewrite_once(val, rules)
            if changed:
                setattr(expr, field, new_val)
                return True, expr
    return False, expr

def evaluate_constants(expr):
    if isinstance(expr, Add):
        l, r = evaluate_constants(expr.left), evaluate_constants(expr.right)
        if isinstance(l, Const) and isinstance(r, Const): return Const(l.value + r.value)
        return Add(l, r)
    if isinstance(expr, Mul):
        l, r = evaluate_constants(expr.left), evaluate_constants(expr.right)
        if isinstance(l, Const) and isinstance(r, Const): return Const(l.value * r.value)
        return Mul(l, r)
    if isinstance(expr, Sub):
        l, r = evaluate_constants(expr.left), evaluate_constants(expr.right)
        if isinstance(l, Const) and isinstance(r, Const): return Const(l.value - r.value)
        return Sub(l, r)
    if isinstance(expr, Div):
        l, r = evaluate_constants(expr.left), evaluate_constants(expr.right)
        if isinstance(l, Const) and isinstance(r, Const): return Const(l.value / r.value)
        return Div(l, r)
    if isinstance(expr, Pow):
        b, e = evaluate_constants(expr.base), evaluate_constants(expr.exp)
        if isinstance(b, Const) and isinstance(e, Const): return Const(b.value ** e.value)
        return Pow(b, e)
    return expr
