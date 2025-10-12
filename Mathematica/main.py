from .expr import *
from .differentiate import differentiate
from .logger import total_steps

x = Var("x")
expr = Add(
    Add(Mul(Const(3), Pow(x, Const(2))), Const(4)),
    Add(Exp(Mul(Const(2), x)),
        Add(Log(x),
            Add(Sin(x),
                Add(Cos(x), Tan(x))))))
print("Expr:", expr)
d = differentiate(expr, "x")
print("Differentiate:", d)
print(f"Total rewrite steps logged: {total_steps()}")
