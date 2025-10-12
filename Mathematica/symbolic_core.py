# symbolic_core.py
# ------------------------------------------------------------
# Symbolic algebra system with pattern-matching rewrite rules
# + full differentiation evaluation (differentiate)
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

@dataclass
class Differentiate(Expr):
    expr: Expr
    var: Var
    def children(self): return [self.expr, self.var]
    def __repr__(self): return f"d/d{self.var}({self.expr})"

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

    # Pattern variable matches anything
    if isinstance(pattern, PatternVar):
        if pattern.name in bindings:
            return bindings if bindings[pattern.name] == expr else None
        bindings[pattern.name] = expr
        return bindings

    # Same node type required
    if type(pattern) is not type(expr):
        return None

    # Const: allow Const(PatternVar(...)) to bind numeric value
    if isinstance(pattern, Const):
        pv = pattern.value
        if isinstance(pv, PatternVar):
            # bind that pattern var name to a Const of expr.value
            if pv.name in bindings:
                return bindings if bindings[pv.name] == expr else None
            bindings[pv.name] = expr  # bind to the whole Const(...)
            return bindings
        return bindings if pattern.value == expr.value else None

    # Var: allow Var(PatternVar(...)) to bind any variable
    if isinstance(pattern, Var):
        pn = pattern.name
        if isinstance(pn, PatternVar):
            if pn.name in bindings:
                return bindings if bindings[pn.name] == expr else None
            bindings[pn.name] = expr  # bind to Var(name)
            return bindings
        return bindings if pattern.name == expr.name else None

    # Recurse on children
    for p_child, e_child in zip(pattern.children(), expr.children()):
        bindings = match(p_child, e_child, bindings)
        if bindings is None:
            return None
    return bindings

def substitute(expr: Expr, bindings: Dict[str, Expr]) -> Expr:
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

    for field in getattr(expr, "__dataclass_fields__", {}):
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
# Simplification Rules
# ============================================================

def simplification_rules() -> List[Tuple[Expr, Expr]]:
    return [
        (Add(PatternVar("x"), Const(0)), PatternVar("x")),
        (Add(Const(0), PatternVar("x")), PatternVar("x")),
        (Sub(PatternVar("x"), Const(0)), PatternVar("x")),
        (Mul(PatternVar("x"), Const(1)), PatternVar("x")),
        (Mul(Const(1), PatternVar("x")), PatternVar("x")),
        (Mul(PatternVar("x"), Const(0)), Const(0)),
        (Mul(Const(0), PatternVar("x")), Const(0)),
    ]

# ============================================================
# Differentiation
# ============================================================

def differentiate(expr: Expr, var: str) -> Expr:
    v = Var(var)
    diff_rules = [
        # constants and variables
        (Differentiate(Const(PatternVar("c")), Var(PatternVar("vv"))), Const(0)),
        (Differentiate(Var(var), Var(var)), Const(1)),
        (Differentiate(Var(PatternVar("x")), Var(var)), Const(0)),

        # linearity
        (Differentiate(Add(PatternVar("u"), PatternVar("w")), Var(var)),
            Add(Differentiate(PatternVar("u"), Var(var)), Differentiate(PatternVar("w"), Var(var)))),
        (Differentiate(Sub(PatternVar("u"), PatternVar("w")), Var(var)),
            Sub(Differentiate(PatternVar("u"), Var(var)), Differentiate(PatternVar("w"), Var(var)))),

        # product rule
        (Differentiate(Mul(PatternVar("u"), PatternVar("w")), Var(var)),
            Add(Mul(Differentiate(PatternVar("u"), Var(var)), PatternVar("w")),
                Mul(PatternVar("u"), Differentiate(PatternVar("w"), Var(var))))),

        # power rule with constant exponent n
        (Differentiate(Pow(PatternVar("u"), Const(PatternVar("n"))), Var(var)),
            Mul(Const(PatternVar("n")),
                Mul(Pow(PatternVar("u"), Sub(Const(PatternVar("n")), Const(1))),
                    Differentiate(PatternVar("u"), Var(var)))))
    ]

    # Expand until all Differentiate nodes are resolved
    result = Differentiate(expr, v)
    prev = None
    while prev != repr(result):
        prev = repr(result)
        result = rewrite(result, diff_rules)
        result = rewrite(result, simplification_rules())
    return result

# ============================================================
# Test Section
# ============================================================

if __name__ == "__main__":
    x = Var("x")

    # Example 1
    expr1 = Mul(Add(x, Const(2)), x)  # (x + 2)*x
    print("Expr 1:", expr1)
    d1 = differentiate(expr1, "x")
    print("Differentiate 1:", d1)
    print("-----")

    # Example 2
    expr2 = Pow(Add(Mul(Const(3), x), Const(4)), Const(2))  # (3x + 4)^2
    print("Expr 2:", expr2)
    d2 = differentiate(expr2, "x")
    print("Differentiate 2:", d2)
