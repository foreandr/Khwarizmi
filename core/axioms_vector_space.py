# ------------------------------------------------------------
# Vector-Space Axioms as Rewrite Rules
# ------------------------------------------------------------
from .expr import *
from .rules import Rule, register_rule

# Example: Distributivity of scalar multiplication over addition
def rule_distrib(expr: Expr):
    if isinstance(expr, ScalarMul) and isinstance(expr.vector, Add):
        a = expr.scalar
        u, v = expr.vector.left, expr.vector.right
        return Add(ScalarMul(a, u), ScalarMul(a, v))
    return None

register_rule(Rule(
    name="VS_Distrib",
    description="Scalar multiplication distributes over vector addition",
    apply=rule_distrib
))
