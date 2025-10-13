# symbolic_math.py

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple, Optional
import os
from logger import log_step, reset_log, get_step_counter, LOG_FILE # Import from logger.py

# ============================================================
# Expression Classes
# ============================================================

class Expr:
    def children(self): return []
    def __repr__(self): raise NotImplementedError
    def __eq__(self, other): return isinstance(other, Expr) and repr(self) == repr(other)

@dataclass
class Const(Expr):
    value: Any
    def __repr__(self): return str(self.value)

@dataclass
class Var(Expr):
    name: Any
    def __repr__(self): return str(self.name)

@dataclass
class Add(Expr):
    left: Expr; right: Expr
    def children(self): return [self.left, self.right]
    def __repr__(self): return f"({self.left}+{self.right})"

@dataclass
class Sub(Expr):
    left: Expr; right: Expr
    def children(self): return [self.left, self.right]
    def __repr__(self): return f"({self.left}-{self.right})"

@dataclass
class Mul(Expr):
    left: Expr; right: Expr
    def children(self): return [self.left, self.right]
    def __repr__(self): return f"({self.left}*{self.right})"

@dataclass
class Div(Expr):
    left: Expr; right: Expr
    def children(self): return [self.left, self.right]
    def __repr__(self): return f"({self.left}/{self.right})"

@dataclass
class Pow(Expr):
    base: Expr; exp: Expr
    def children(self): return [self.base, self.exp]
    def __repr__(self): return f"({self.base}^{self.exp})"

@dataclass
class Exp(Expr):
    arg: Expr
    def children(self): return [self.arg]
    def __repr__(self): return f"exp({self.arg})"

@dataclass
class Log(Expr):
    arg: Expr
    def children(self): return [self.arg]
    def __repr__(self): return f"log({self.arg})"

@dataclass
class Sin(Expr):
    arg: Expr
    def children(self): return [self.arg]
    def __repr__(self): return f"sin({self.arg})"

@dataclass
class Cos(Expr):
    arg: Expr
    def children(self): return [self.arg]
    def __repr__(self): return f"cos({self.arg})"

@dataclass
class Tan(Expr):
    arg: Expr
    def children(self): return [self.arg]
    def __repr__(self): return f"tan({self.arg})"

@dataclass
class ArcSin(Expr):
    arg: Expr
    def children(self): return [self.arg]
    def __repr__(self): return f"arcsin({self.arg})"

@dataclass
class ArcCos(Expr):
    arg: Expr
    def children(self): return [self.arg]
    def __repr__(self): return f"arccos({self.arg})"

@dataclass
class ArcTan(Expr):
    arg: Expr
    def children(self): return [self.arg]
    def __repr__(self): return f"arctan({self.arg})"

@dataclass
class Sqrt(Expr):
    arg: Expr
    def children(self): return [self.arg]
    def __repr__(self): return f"sqrt({self.arg})"


@dataclass
class Differentiate(Expr):
    expr: Expr; var: Var
    def children(self): return [self.expr, self.var]
    def __repr__(self): return f"d/d{self.var}({self.expr})"

@dataclass
class PatternVar(Expr):
    name: str
    def __repr__(self): return f"?{self.name}"

@dataclass
class Neg(Expr):
    arg: Expr
    def children(self): return [self.arg]
    def __repr__(self): return f"(-{self.arg})"

@dataclass
class Sec(Expr):
    arg: Expr
    def children(self): return [self.arg]
    def __repr__(self): return f"sec({self.arg})"

@dataclass
class Csc(Expr):
    arg: Expr
    def children(self): return [self.arg]
    def __repr__(self): return f"csc({self.arg})"

@dataclass
class Cot(Expr):
    arg: Expr
    def children(self): return [self.arg]
    def __repr__(self): return f"cot({self.arg})"

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
                # FIX: Use field_names list to collect current arguments
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