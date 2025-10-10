# ------------------------------------------------------------
# Vector Space Axioms — registered as rewrite rules
# ------------------------------------------------------------
from .expr import *
from .rules import Rule, register_rule

# ------------------------------------------------------------
# Axioms implemented as rewrite transformations
# ------------------------------------------------------------

def axiom_add_comm(expr):
    # u + v → v + u
    if isinstance(expr, Add):
        return Add(expr.right, expr.left)
    return None


def axiom_add_assoc(expr):
    # (u + v) + w → u + (v + w)
    if isinstance(expr, Add) and isinstance(expr.left, Add):
        return Add(expr.left.left, Add(expr.left.right, expr.right))
    return None


def axiom_add_id(expr):
    # u + 0 → u
    if isinstance(expr, Add) and isinstance(expr.right, Const) and expr.right.value == 0:
        return expr.left
    return None


def axiom_add_inv(expr):
    # u + (-u) → 0
    if isinstance(expr, Add) and isinstance(expr.right, Mul):
        if isinstance(expr.right.left, Const) and expr.right.left.value == -1:
            if str(expr.left) == str(expr.right.right):
                return Const(0)
    return None


def axiom_scalar_distrib_vector(expr):
    # a · (u + v) → (a · u + a · v)
    if isinstance(expr, ScalarMul) and isinstance(expr.vector, Add):
        return Add(ScalarMul(expr.scalar, expr.vector.left),
                   ScalarMul(expr.scalar, expr.vector.right))
    return None


def axiom_scalar_distrib_scalar(expr):
    # (a + b) · u → (a · u + b · u)
    if isinstance(expr, ScalarMul) and isinstance(expr.scalar, Add):
        return Add(ScalarMul(expr.scalar.left, expr.vector),
                   ScalarMul(expr.scalar.right, expr.vector))
    return None


def axiom_scalar_assoc(expr):
    # a · (b · u) → (a·b) · u
    if isinstance(expr, ScalarMul) and isinstance(expr.vector, ScalarMul):
        return ScalarMul(Mul(expr.scalar, expr.vector.scalar), expr.vector.vector)
    return None


def axiom_scalar_id(expr):
    # 1 · u → u
    if isinstance(expr, ScalarMul) and isinstance(expr.scalar, Const) and expr.scalar.value == 1:
        return expr.vector
    return None


# ------------------------------------------------------------
# Register all axioms
# ------------------------------------------------------------

register_rule(Rule("VS_Add_Comm", "Addition is commutative", axiom_add_comm))
register_rule(Rule("VS_Add_Assoc", "Addition is associative", axiom_add_assoc))
register_rule(Rule("VS_Add_Id", "Additive identity", axiom_add_id))
register_rule(Rule("VS_Add_Inv", "Additive inverse", axiom_add_inv))
register_rule(Rule("VS_Distrib_Vector", "Scalar multiplication distributes over vector addition", axiom_scalar_distrib_vector))
register_rule(Rule("VS_Distrib_Scalar", "Scalar multiplication distributes over scalar addition", axiom_scalar_distrib_scalar))
register_rule(Rule("VS_Scalar_Assoc", "Scalar multiplication associative", axiom_scalar_assoc))
register_rule(Rule("VS_Scalar_Id", "Scalar multiplication identity", axiom_scalar_id))
