# symbolic_core.py
# ------------------------------------------------------------
# Symbolic algebra system with pattern-matching rewrite rules
# (with numeric constant evaluation and working simplification)
# ------------------------------------------------------------

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple, Optional

# ============================================================
# Expression Classes
# ============================================================

class Expr:
    def children(self):
        return []
    def __repr__(self):
        raise NotImplementedError
    def __eq__(self, other):
        return isinstance(other, Expr) and repr(self) == repr(other)

@dataclass
class Const(Expr):
    value: Any
    def __repr__(self):
        return str(self.value)

@dataclass
class Var(Expr):
    name: str
    def __repr__(self):
        return self.name

@dataclass
class Add(Expr):
    left: Expr
    right: Expr
    def children(self): return [self.left, self.right]
    def __repr__(self): return f"({self.left}+{self.right})"

@dataclass
class Sub(Expr):
    left: Expr
    right: Expr
    def children(self): return [self.left, self.right]
    def __repr__(self): return f"({self.left}-{self.right})"

@dataclass
class Mul(Expr):
    left: Expr
    right: Expr
    def children(self): return [self.left, self.right]
    def __repr__(self): return f"({self.left}*{self.right})"

@dataclass
class Div(Expr):
    left: Expr
    right: Expr
    def children(self): return [self.left, self.right]
    def __repr__(self): return f"({self.left}/{self.right})"

@dataclass
class Pow(Expr):
    base: Expr
    exp: Expr
    def children(self): return [self.base, self.exp]
    def __repr__(self): return f"({self.base}^{self.exp})"

# ============================================================
# Pattern Variable
# ============================================================

@dataclass
class PatternVar(Expr):
    name: str
    def __repr__(self): return f"?{self.name}"

# ============================================================
# Pattern Matching and Substitution
# ============================================================

def match(pattern: Expr, expr: Expr, bindings: Optional[Dict[str, Expr]] = None) -> Optional[Dict[str, Expr]]:
    if bindings is None: bindings = {}

    if isinstance(pattern, PatternVar):
        if pattern.name in bindings:
            if bindings[pattern.name] == expr:
                return bindings
            return None
        bindings[pattern.name] = expr
        return bindings

    if type(pattern) is not type(expr):
        return None

    if isinstance(pattern, Const):
        return bindings if pattern.value == expr.value else None
    if isinstance(pattern, Var):
        return bindings if pattern.name == expr.name else None

    for p_child, e_child in zip(pattern.children(), expr.children()):
        bindings = match(p_child, e_child, bindings)
        if bindings is None:
            return None

    return bindings

def substitute(expr: Expr, bindings: Dict[str, Expr]) -> Expr:
    if isinstance(expr, PatternVar):
        return bindings.get(expr.name, expr)
    if isinstance(expr, Const) or isinstance(expr, Var):
        return expr
    args = [substitute(child, bindings) for child in expr.children()]
    return type(expr)(*args)

# ============================================================
# Rewrite Engine
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
            return True, new_expr

    for field in expr.__dataclass_fields__:
        val = getattr(expr, field)
        if isinstance(val, Expr):
            changed, new_val = _rewrite_once(val, rules)
            if changed:
                setattr(expr, field, new_val)
                return True, expr
    return False, expr

# ============================================================
# Constant Folding
# ============================================================

def evaluate_constants(expr: Expr) -> Expr:
    if isinstance(expr, Add):
        left, right = evaluate_constants(expr.left), evaluate_constants(expr.right)
        if isinstance(left, Const) and isinstance(right, Const):
            return Const(left.value + right.value)
        return Add(left, right)
    if isinstance(expr, Mul):
        left, right = evaluate_constants(expr.left), evaluate_constants(expr.right)
        if isinstance(left, Const) and isinstance(right, Const):
            return Const(left.value * right.value)
        return Mul(left, right)
    if isinstance(expr, Sub):
        left, right = evaluate_constants(expr.left), evaluate_constants(expr.right)
        if isinstance(left, Const) and isinstance(right, Const):
            return Const(left.value - right.value)
        return Sub(left, right)
    if isinstance(expr, Div):
        left, right = evaluate_constants(expr.left), evaluate_constants(expr.right)
        if isinstance(left, Const) and isinstance(right, Const):
            return Const(left.value / right.value)
        return Div(left, right)
    if isinstance(expr, Pow):
        base, exp = evaluate_constants(expr.base), evaluate_constants(expr.exp)
        if isinstance(base, Const) and isinstance(exp, Const):
            return Const(base.value ** exp.value)
        return Pow(base, exp)
    return expr

# ============================================================
# Test Section
# ============================================================

if __name__ == "__main__":
    x = Var("x")
    expr = Add(Mul(Const(2), Const(3)), Mul(Const(1), x))
    print("Before:", expr)

    rules = [
        (Add(PatternVar("x"), Const(0)), PatternVar("x")),
        (Add(Const(0), PatternVar("x")), PatternVar("x")),
        (Mul(PatternVar("x"), Const(1)), PatternVar("x")),
        (Mul(Const(1), PatternVar("x")), PatternVar("x")),
        (Mul(PatternVar("x"), Const(0)), Const(0)),
        (Mul(Const(0), PatternVar("x")), Const(0)),
    ]

    simplified = rewrite(expr, rules)
    print("After:", simplified)
