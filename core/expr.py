# ------------------------------------------------------------
# core/expr.py
# ------------------------------------------------------------
# Expression Tree Definitions for the Symbolic Manipulation System
# Each class represents a symbolic expression node and defines
# a .to_latex() method for exporting to readable LaTeX.
# ------------------------------------------------------------

from dataclasses import dataclass
from typing import Any


class Expr:
    """Base class for all symbolic expressions."""
    def to_latex(self) -> str:
        raise NotImplementedError

    def __str__(self):
        return self.to_latex()


# ---------- Atomic Expressions ----------

@dataclass
class Const(Expr):
    value: Any
    def to_latex(self):
        return str(self.value)


@dataclass
class Var(Expr):
    name: str
    def to_latex(self):
        return self.name


# ---------- Composite Expressions ----------

@dataclass
class Add(Expr):
    left: Expr
    right: Expr
    def to_latex(self):
        return f"({self.left.to_latex()} + {self.right.to_latex()})"


@dataclass
class Sub(Expr):
    left: Expr
    right: Expr
    def to_latex(self):
        return f"({self.left.to_latex()} - {self.right.to_latex()})"


@dataclass
class Mul(Expr):
    left: Expr
    right: Expr
    def to_latex(self):
        # Use \cdot instead of literal dot so it works in math mode
        return f"{self.left.to_latex()} \\cdot {self.right.to_latex()}"


@dataclass
class ScalarMul(Expr):
    scalar: Expr
    vector: Expr
    def to_latex(self):
        # Also use \cdot for proper LaTeX rendering
        return f"{self.scalar.to_latex()} \\cdot {self.vector.to_latex()}"


@dataclass
class Pow(Expr):
    base: Expr
    exponent: Expr
    def to_latex(self):
        return f"{self.base.to_latex()}^{{{self.exponent.to_latex()}}}"


@dataclass
class Eq(Expr):
    left: Expr
    right: Expr
    def to_latex(self):
        return f"{self.left.to_latex()} = {self.right.to_latex()}"
