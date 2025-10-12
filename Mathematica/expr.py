from dataclasses import dataclass

# ------------------------------------------------------------
# Expression Tree Definitions
# ------------------------------------------------------------

class Expr:
    def children(self):
        return []
    def __repr__(self):
        raise NotImplementedError
    def __eq__(self, other):
        return isinstance(other, Expr) and repr(self) == repr(other)

@dataclass
class Const(Expr):
    value: any
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
    def children(self):
        return [self.left, self.right]
    def __repr__(self):
        return f"({self.left}+{self.right})"

@dataclass
class Sub(Expr):
    left: Expr
    right: Expr
    def children(self):
        return [self.left, self.right]
    def __repr__(self):
        return f"({self.left}-{self.right})"

@dataclass
class Mul(Expr):
    left: Expr
    right: Expr
    def children(self):
        return [self.left, self.right]
    def __repr__(self):
        return f"({self.left}*{self.right})"

@dataclass
class Div(Expr):
    left: Expr
    right: Expr
    def children(self):
        return [self.left, self.right]
    def __repr__(self):
        return f"({self.left}/{self.right})"

@dataclass
class Pow(Expr):
    base: Expr
    exp: Expr
    def children(self):
        return [self.base, self.exp]
    def __repr__(self):
        return f"({self.base}^{self.exp})"

# Unary functions
@dataclass
class Exp(Expr):
    arg: Expr
    def children(self):
        return [self.arg]
    def __repr__(self):
        return f"exp({self.arg})"

@dataclass
class Log(Expr):
    arg: Expr
    def children(self):
        return [self.arg]
    def __repr__(self):
        return f"log({self.arg})"

@dataclass
class Sin(Expr):
    arg: Expr
    def children(self):
        return [self.arg]
    def __repr__(self):
        return f"sin({self.arg})"

@dataclass
class Cos(Expr):
    arg: Expr
    def children(self):
        return [self.arg]
    def __repr__(self):
        return f"cos({self.arg})"

@dataclass
class Tan(Expr):
    arg: Expr
    def children(self):
        return [self.arg]
    def __repr__(self):
        return f"tan({self.arg})"

@dataclass
class Differentiate(Expr):
    expr: Expr
    var: Var
    def children(self):
        return [self.expr, self.var]
    def __repr__(self):
        return f"d/d{self.var}({self.expr})"
