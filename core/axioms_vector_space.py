# ------------------------------------------------------------
# Vector Space Axioms — registered as rewrite rules
# ------------------------------------------------------------
from .expr import *
from .rules import Rule, register_rule

# ------------------------------------------------------------
# Axioms implemented as rewrite transformations
# ------------------------------------------------------------

def axiom_add_comm(expr):
    # u + v → v + u (Only if str(u) > str(v) to enforce canonical order)
    if isinstance(expr, Add):
        # FIX: Enforce canonical order to prevent infinite loops
        if str(expr.left) > str(expr.right):
            # Transform to v + u
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
    # FIX: Must check for ScalarMul, not Mul, based on expr.py definitions
    if isinstance(expr, Add) and isinstance(expr.right, ScalarMul):
        if isinstance(expr.right.scalar, Const) and expr.right.scalar.value == -1:
            if str(expr.left) == str(expr.right.vector):
                return Const(0)
    return None


def axiom_scalar_distrib_vector(expr):
    # a · (u + v) → a · u + a · v
    if isinstance(expr, ScalarMul) and isinstance(expr.vector, Add):
        return Add(ScalarMul(expr.scalar, expr.vector.left),
                   ScalarMul(expr.scalar, expr.vector.right))
    return None


def axiom_scalar_distrib_scalar(expr):
    # (a + b) · u → a · u + b · u
    if isinstance(expr, ScalarMul) and isinstance(expr.scalar, Add):
        return Add(ScalarMul(expr.scalar.left, expr.vector),
                   ScalarMul(expr.scalar.right, expr.vector))
    return None


def axiom_scalar_assoc(expr):
    # a · (b · u) → (a·b) · u
    # This rule is the focus of Test 6.
    if isinstance(expr, ScalarMul) and isinstance(expr.vector, ScalarMul):
        # Step 1: Group the scalars (a·b)
        new_scalar = Mul(expr.scalar, expr.vector.scalar)
        new_vector = expr.vector.vector
        # Return the new structure: (a·b) · u
        return ScalarMul(new_scalar, new_vector)
    return None


def axiom_scalar_id(expr):
    # 1 · u → u
    if isinstance(expr, ScalarMul) and isinstance(expr.scalar, Const) and expr.scalar.value == 1:
        return expr.vector
    return None


def axiom_zero_mul(expr):
    # 0 · u → 0
    if isinstance(expr, ScalarMul) and isinstance(expr.scalar, Const) and expr.scalar.value == 0:
        return Const(0)
    return None


# --- NEW RULES FOR COMPLEX TESTS ---

def axiom_factor_scalar(expr):
    # a · u + b · u → (a + b) · u
    if isinstance(expr, Add):
        left = expr.left
        right = expr.right
        
        # Check if left is a · u and right is b · u
        if isinstance(left, ScalarMul) and isinstance(right, ScalarMul):
            if str(left.vector) == str(right.vector):
                # Found a·u + b·u
                new_scalar = Add(left.scalar, right.scalar)
                return ScalarMul(new_scalar, left.vector)
    return None
    
def axiom_scalar_arith(expr):
    # Perform simple constant arithmetic: a + b -> c or a * b -> c
    # CRITICAL: This is the rule that turns (-1 \cdot -1) into 1.
    if isinstance(expr, Add):
        if isinstance(expr.left, Const) and isinstance(expr.right, Const):
            return Const(expr.left.value + expr.right.value)
    if isinstance(expr, Mul):
        if isinstance(expr.left, Const) and isinstance(expr.right, Const):
            return Const(expr.left.value * expr.right.value)
    return None


# ------------------------------------------------------------
# Register all axioms - PRIORITY ORDERING IS CRITICAL FOR TERMINATION
# ------------------------------------------------------------

# 0. Scalar Arithmetic (Highest Priority - Simplify constants immediately)
# This MUST run before VS_Scalar_Id, and often immediately after VS_Scalar_Assoc
register_rule(Rule("Scalar_Arith", "Perform scalar constant arithmetic (e.g., a+b or a*b)", axiom_scalar_arith))

# 1. Elimination/Identity Rules (Remove terms)
register_rule(Rule("VS_Zero_Mul", "Multiplication by zero scalar or zero vector is zero", axiom_zero_mul))
register_rule(Rule("VS_Scalar_Id", "Scalar multiplication identity (1 · u -> u)", axiom_scalar_id))
register_rule(Rule("VS_Add_Inv", "Additive inverse (u + (-1)u -> 0)", axiom_add_inv))
register_rule(Rule("VS_Add_Id", "Additive identity (u + 0 -> u)", axiom_add_id))
register_rule(Rule("VS_Factor_Scalar", "Distributivity: a·u + b·u -> (a+b)·u", axiom_factor_scalar))

# 2. Structural Expansion Rules
register_rule(Rule("VS_Distrib_Vector", "Scalar multiplication distributes over vector addition", axiom_scalar_distrib_vector))
register_rule(Rule("VS_Distrib_Scalar", "Scalar multiplication distributes over scalar addition", axiom_scalar_distrib_scalar))
# VS_Scalar_Assoc must be here to fire when the simplify loop recurses
register_rule(Rule("VS_Scalar_Assoc", "Scalar multiplication associative", axiom_scalar_assoc))


# 3. Canonicalization Rules (Lowest Priority - Must not cause loops with higher priority rules)
register_rule(Rule("VS_Add_Assoc", "Addition is associative (enforcing right-deep)", axiom_add_assoc))
register_rule(Rule("VS_Add_Comm", "Addition is commutative (canonicalized)", axiom_add_comm))