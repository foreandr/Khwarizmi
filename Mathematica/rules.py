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
    # The original implementation only recursed for binary ops, which is fine for this constant folding set,
    # but for completeness, unary functions would also need to be checked if they contain constants.
    # Since the original didn't include it, I'll keep the constant folding as is.
    return expr

# ============================================================
# Simplification Rules
# ============================================================
def simplification_rules() -> List[Tuple[Expr, Expr]]:
    return [
        # ---------- Algebraic base identities ----------
        (Add(PatternVar("x"), Const(0)), PatternVar("x")),
        (Add(Const(0), PatternVar("x")), PatternVar("x")),
        (Sub(PatternVar("x"), Const(0)), PatternVar("x")),
        (Mul(PatternVar("x"), Const(1)), PatternVar("x")),
        (Mul(Const(1), PatternVar("x")), PatternVar("x")),
        (Mul(PatternVar("x"), Const(0)), Const(0)),
        (Mul(Const(0), PatternVar("x")), Const(0)),
        (Pow(PatternVar("x"), Const(1)), PatternVar("x")),
        (Pow(PatternVar("x"), Const(0)), Const(1)),
        (Div(PatternVar("x"), Const(1)), PatternVar("x")),

        # ---------- Negation simplifications ----------
        (Neg(Const(0)), Const(0)),
        (Neg(Const(-1)), Const(1)),
        (Neg(Const(1)), Const(-1)),
        (Neg(Neg(PatternVar("x"))), PatternVar("x")),
        (Mul(Const(-1), PatternVar("x")), Neg(PatternVar("x"))),
        (Mul(PatternVar("x"), Const(-1)), Neg(PatternVar("x"))),
        (Add(PatternVar("x"), Neg(PatternVar("x"))), Const(0)),
        (Sub(PatternVar("x"), PatternVar("x")), Const(0)),

        # ---------- Reciprocal trig identities ----------
        (Sec(PatternVar("u")), Div(Const(1), Cos(PatternVar("u")))),
        (Csc(PatternVar("u")), Div(Const(1), Sin(PatternVar("u")))),
        (Cot(PatternVar("u")), Div(Cos(PatternVar("u")), Sin(PatternVar("u")))),

        # ---------- Canonical trig identities ----------
        # tan^2(u) + 1  →  1 / cos^2(u)
        (Add(Pow(Tan(PatternVar("u")), Const(2)), Const(1)),
         Div(Const(1), Pow(Cos(PatternVar("u")), Const(2)))),
        (Add(Const(1), Pow(Tan(PatternVar("u")), Const(2))),
         Div(Const(1), Pow(Cos(PatternVar("u")), Const(2)))),

        # 1 / cos^2(u)  →  sec^2(u)
        (Div(Const(1), Pow(Cos(PatternVar("u")), Const(2))),
         Pow(Sec(PatternVar("u")), Const(2))),

        (Sub(Const(0), PatternVar("x")), Mul(Const(-1), PatternVar("x"))),
        (Sub(Const(0), Mul(Const(-1), PatternVar("x"))), PatternVar("x")),

        (Add(Const(0), PatternVar("x")), PatternVar("x")),
        (Add(PatternVar("x"), Const(0)), PatternVar("x")),
        (Sub(PatternVar("x"), Const(0)), PatternVar("x")),

        (Sub(Const(0), PatternVar("x")), Mul(Const(-1), PatternVar("x"))),
        (Sub(Const(0), Mul(Const(-1), PatternVar("x"))), PatternVar("x")),
        (Div(Sin(PatternVar("u")), Cos(PatternVar("u"))), Tan(PatternVar("u"))),

        # ---------- Negation simplifications ----------
        # (-(-x)) → x
        (Mul(Const(-1), Mul(Const(-1), PatternVar("x"))), PatternVar("x")),
        # (-(-1)) → 1
        (Mul(Const(-1), Const(-1)), Const(1)),
        # (-(-expr)) → expr (pattern form)
        # (-(-expr)) → expr (pattern form)
        (Sub(Const(0), Sub(Const(0), PatternVar("x"))), PatternVar("x")),

        # sin(x)/cos(x)^2  →  (1/cos(x))*tan(x)
        (
            Div(Sin(PatternVar("u")), Pow(Cos(PatternVar("u")), Const(2))),
            Mul(Div(Const(1), Cos(PatternVar("u"))), Tan(PatternVar("u")))
        ),

    ]


# ============================================================
# Differentiation
# ============================================================

def differentiate(expr: Expr, var: str) -> Expr:
    reset_log()
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

        # product / quotient
        (Differentiate(Mul(PatternVar("u"), PatternVar("w")), Var(var)),
            Add(Mul(Differentiate(PatternVar("u"), Var(var)), PatternVar("w")),
                Mul(PatternVar("u"), Differentiate(PatternVar("w"), Var(var))))),
        (Differentiate(Div(PatternVar("u"), PatternVar("w")), Var(var)),
            Div(Sub(Mul(Differentiate(PatternVar("u"), Var(var)), PatternVar("w")),
                      Mul(PatternVar("u"), Differentiate(PatternVar("w"), Var(var)))),
                Pow(PatternVar("w"), Const(2)))),

        # power rule with constant exponent
        (Differentiate(Pow(PatternVar("u"), Const(PatternVar("n"))), Var(var)),
            Mul(Const(PatternVar("n")),
                Mul(Pow(PatternVar("u"), Sub(Const(PatternVar("n")), Const(1))),
                    Differentiate(PatternVar("u"), Var(var))))),

        # exp / log
        (Differentiate(Exp(PatternVar("u")), Var(var)),
            Mul(Exp(PatternVar("u")), Differentiate(PatternVar("u"), Var(var)))),
        (Differentiate(Log(PatternVar("u")), Var(var)),
            Div(Differentiate(PatternVar("u"), Var(var)), PatternVar("u"))),

        # trig
        (Differentiate(Sin(PatternVar("u")), Var(var)),
            Mul(Cos(PatternVar("u")), Differentiate(PatternVar("u"), Var(var)))),
        (Differentiate(Cos(PatternVar("u")), Var(var)),
            Mul(Const(-1), Mul(Sin(PatternVar("u")), Differentiate(PatternVar("u"), Var(var))))),
        (Differentiate(Tan(PatternVar("u")), Var(var)),
            Mul(Div(Const(1), Pow(Cos(PatternVar("u")), Const(2))), Differentiate(PatternVar("u"), Var(var)))),

        # ----- Unary negation -----
        (Differentiate(Neg(PatternVar("u")), Var(var)),
        Neg(Differentiate(PatternVar("u"), Var(var)))),

        # ----- Reciprocal trigonometric functions -----
        (Differentiate(Sec(PatternVar("u")), Var(var)),
        Mul(Sec(PatternVar("u")),
            Mul(Tan(PatternVar("u")),
                Differentiate(PatternVar("u"), Var(var))))),

        (Differentiate(Csc(PatternVar("u")), Var(var)),
        Neg(Mul(Csc(PatternVar("u")),
                Mul(Cot(PatternVar("u")),
                    Differentiate(PatternVar("u"), Var(var)))))),

        (Differentiate(Cot(PatternVar("u")), Var(var)),
        Neg(Mul(Div(Const(1), Pow(Sin(PatternVar("u")), Const(2))),
                Differentiate(PatternVar("u"), Var(var))))),


    ]
    result = Differentiate(expr, v)
    prev = None
    while prev != repr(result):
        prev = repr(result)
        result = rewrite(result, diff_rules)
        result = rewrite(result, simplification_rules())
    return result

