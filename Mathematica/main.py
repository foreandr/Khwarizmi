import os
from logger import log_step, reset_log, get_step_counter, LOG_FILE # Import from logger.py
from rules import *

# ============================================================
# Test Section
# ============================================================

if __name__ == "__main__":
    x = Var("x")

    # 3*x^2 + 4 + exp(2*x) + log(x) + sin(x) + cos(x) + tan(x)
    expr = Add(
        Add(Mul(Const(3), Pow(x, Const(2))), Const(4)),
        Add(Exp(Mul(Const(2), x)),
            Add(Log(x),
                Add(Sin(x),
                    Add(Cos(x),
                        Tan(x))))))
    print("Expr:", expr)
    d = differentiate(expr, "x")
    print("Differentiate:", d)
    print(f"Total rewrite steps logged: {get_step_counter()}")
    print(f"Log written to: {os.path.abspath(LOG_FILE)}")