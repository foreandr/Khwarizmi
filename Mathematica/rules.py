# rules.py
# (Core symbolic classes and a facade for the engine functions)

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple, Optional
import os # Keep os for compatibility with original imports
from logger import log_step, reset_log, get_step_counter, LOG_FILE # Keep logger imports

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

# --- Inverse Trig ---
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
class ArcCsc(Expr):
    arg: Expr
    def children(self): return [self.arg]
    def __repr__(self): return f"arccsc({self.arg})"

@dataclass
class ArcSec(Expr):
    arg: Expr
    def children(self): return [self.arg]
    def __repr__(self): return f"arcsec({self.arg})"

@dataclass
class ArcCot(Expr):
    arg: Expr
    def children(self): return [self.arg]
    def __repr__(self): return f"arccot({self.arg})"


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
class Integrate(Expr):
    expr: Expr; var: Var
    def children(self): return [self.expr, self.var]
    def __repr__(self): return f"∫d{self.var}({self.expr})"

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

# --- Hyperbolic Functions ---
@dataclass
class Sinh(Expr):
    arg: Expr
    def children(self): return [self.arg]
    def __repr__(self): return f"sinh({self.arg})"

@dataclass
class Cosh(Expr):
    arg: Expr
    def children(self): return [self.arg]
    def __repr__(self): return f"cosh({self.arg})"

@dataclass
class Tanh(Expr):
    arg: Expr
    def children(self): return [self.arg]
    def __repr__(self): return f"tanh({self.arg})"

@dataclass
class Coth(Expr):
    arg: Expr
    def children(self): return [self.arg]
    def __repr__(self): return f"coth({self.arg})"

@dataclass
class Sech(Expr):
    arg: Expr
    def children(self): return [self.arg]
    def __repr__(self): return f"sech({self.arg})"

@dataclass
class Csch(Expr):
    arg: Expr
    def children(self): return [self.arg]
    def __repr__(self): return f"csch({self.arg})"
    
# --- Absolute Value ---
@dataclass
class Abs(Expr):
    arg: Expr
    def children(self): return [self.arg]
    def __repr__(self): return f"abs({self.arg})"

# ============================================================
# FACADE / PUBLIC API
# Import and re-export the engine functions to maintain compatibility.
# All existing files will still be able to "from rules import rewrite"
# ============================================================
from engine import match, substitute, rewrite, evaluate_constants