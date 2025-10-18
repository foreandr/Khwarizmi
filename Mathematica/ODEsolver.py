# ODEsolver.py (Adding Separable-g(x)h(y) solver)

from rules import Var, Const, Add, Mul, Pow, Exp, Log, Sin, Cos, Sub, Div, Neg, Expr, Abs # Need Abs for integration
from integration import integrate
from ODEclassifier import classify_first_order
from utils import is_independent_of # CRITICAL: Needed for decomposition
from logger import reset_log, log_step, get_step_counter, LOG_FILE  
from simplification import rewrite, simplification_rules, evaluate_constants

# New symbolic class to represent the derivative dy/dx.
class DyDx(Expr):
    """Represents the first derivative dy/dx."""
    def __init__(self, var: str = "y", wrt: str = "x"):
        self.var = Var(var)
        self.wrt = Var(wrt)
    def children(self): return [self.var, self.wrt]
    def __repr__(self): return f"d{self.var}/d{self.wrt}"
    # Use repr() for equality check because DyDx doesn't have child nodes that need recursive checking
    def __eq__(self, other):
        return isinstance(other, DyDx) and repr(self) == repr(other)
    
# Helper function to extract and flatten additive terms.
def flatten_ode_terms(expr):
    """Flattens the ODE expression (LHS = 0) into a list of additive terms."""
    terms = []
    
    # Base Cases: DyDx is now treated as a factor, not just a leaf.
    if isinstance(expr, DyDx):
        return [expr]
    if not isinstance(expr, (Add, Sub, Neg)):
        return [expr]
    
    # Recursive Cases
    if isinstance(expr, Add):
        terms.extend(flatten_ode_terms(expr.left))
        terms.extend(flatten_ode_terms(expr.right))
    elif isinstance(expr, Sub):
        # A - B is treated as A + (-B)
        terms.extend(flatten_ode_terms(expr.left))
        
        # Negate the right term for Subtraction
        right_negated = Neg(expr.right)
        right_negated = rewrite(right_negated, simplification_rules())
        right_negated = evaluate_constants(right_negated)
        terms.append(right_negated)
    elif isinstance(expr, Neg):
        # Handle standalone Negations from earlier steps
        terms.append(expr)

    return terms


def normalize_ode(ode_expr: Expr, dy_dx_marker: DyDx, x_var: str) -> tuple[Expr, Expr, Expr]:
    """
    Takes an ODE expression set to zero, and algebraically solves for dy/dx.
    Transforms F(y', x, y) = 0 into M(x,y) + N(x,y)*y' = 0 and y' = f(x,y).
    
    Returns: (M, N, f_xy)
    """
    log_step(f"Normalizing ODE: solving for {dy_dx_marker}")
    
    # Flatten the LHS into additive terms 
    flat_terms = flatten_ode_terms(ode_expr)

    n_y_prime_term = None # The N * dy/dx term
    m_terms = []          # The M(x,y) terms

    # --- Pass 1: Separate M and N terms ---
    for term in flat_terms:
        is_derivative_term = False
        
        # Case 1: The term is dy/dx itself (N=1)
        if term == dy_dx_marker:
            n_y_prime_term = term
            is_derivative_term = True
            
        # Case 2: The term is N * dy/dx
        elif isinstance(term, Mul):
            # Check if one factor is DyDx
            if term.left == dy_dx_marker:
                n_y_prime_term = term
                is_derivative_term = True
            elif term.right == dy_dx_marker:
                n_y_prime_term = term
                is_derivative_term = True
                
        # Case 3: All other M terms
        if not is_derivative_term:
            m_terms.append(term)

    # --- Pass 2: Extract N and M ---
    
    # Extract N (the coefficient of dy/dx)
    if n_y_prime_term == dy_dx_marker:
        N = Const(1)
    elif isinstance(n_y_prime_term, Mul):
        # The factor that ISN'T dy/dx is N
        if n_y_prime_term.left == dy_dx_marker:
            N = n_y_prime_term.right
        elif n_y_prime_term.right == dy_dx_marker:
            N = n_y_prime_term.left
    else:
        # Should not happen if parsing is correct, but indicates a failure
        log_step("Normalization failed: Could not isolate N*y' term.")
        return None, None, ode_expr
        

    # M is the sum of all remaining terms
    if not m_terms:
        M = Const(0)
    else:
        M = m_terms[0]
        for i in range(1, len(m_terms)):
            M = Add(M, m_terms[i])
        
    # Final cleanup of M and N
    M = rewrite(M, simplification_rules())
    M = evaluate_constants(M)
    N = rewrite(N, simplification_rules())
    N = evaluate_constants(N)


    # Calculate f(x,y) = -M / N (Since M + N*y' = 0 -> y' = -M/N)
    f_xy = Div(Neg(M), N)
    f_xy = rewrite(f_xy, simplification_rules())
    f_xy = evaluate_constants(f_xy)

    log_step(f"Decomposition: M={M}, N={N}")
    log_step(f"Normalized RHS f(x,y): {f_xy}")
    return M, N, f_xy


def solve_separable_fx(f_x: Expr, x_var: str = "x") -> Expr:
    """Solves dy/dx = f(x) by direct integration (y = ∫ f(x) dx + C)."""
    log_step(f"Solving ODE using: Direct Integration (∫ f(x) dx + C)")
    
    # The integration function is now recursively fixed to solve all nested integrals
    integral_result = integrate(f_x, x_var, reset=True)
    
    C = Var("C") 
    solution = Add(integral_result, C)
    return solution

# --- NEW SOLVER IMPLEMENTATION for ODE 2 ---
def solve_separable_gxh(f_xy: Expr, x_var: str = "x", y_var: str = "y") -> str:
    """Solves dy/dx = g(x)h(y) by separating variables (∫ 1/h(y) dy = ∫ g(x) dx + C)."""
    log_step(f"Solving ODE using: Separation of Variables (∫ 1/h(y) dy = ∫ g(x) dx + C)")
    
    x = Var(x_var)
    y = Var(y_var)
    
    # 1. Determine g(x) and h(y) from f_xy (assumes f_xy is Mul/Div form from classifier)
    g_x, h_y = None, None
    if isinstance(f_xy, (Mul, Div)):
        # Check for g(x) * h(y) or h(y) * g(x)
        if is_independent_of(f_xy.left, y) and is_independent_of(f_xy.right, x):
            g_x = f_xy.left
            h_y = f_xy.right
        elif is_independent_of(f_xy.right, y) and is_independent_of(f_xy.left, x):
            g_x = f_xy.right
            h_y = f_xy.left
        
    # Final check for separable function form (should not be needed if classifier is perfect)
    if g_x is None or h_y is None:
        if is_independent_of(f_xy, y): 
             g_x, h_y = f_xy, Const(1) # Already handled by Separable-f(x), but good fallback
        elif is_independent_of(f_xy, x): 
             g_x, h_y = Const(1), f_xy # y' = h(y)
        else:
             return "Classification: Separable-g(x)h(y). Error in g(x)h(y) decomposition."


    # 2. Formulate 1/h(y)
    one_over_h_y = Div(Const(1), h_y)
    one_over_h_y = rewrite(one_over_h_y, simplification_rules())
    one_over_h_y = evaluate_constants(one_over_h_y)
    
    # 3. Integrate LHS (in terms of y)
    lhs_integral = integrate(one_over_h_y, y_var, reset=True)
    
    # 4. Integrate RHS (in terms of x)
    rhs_integral = integrate(g_x, x_var, reset=True)
    
    log_step(f"g(x) = {g_x}, h(y) = {h_y}")
    log_step(f"LHS Integral ∫ (1/h) dy: {lhs_integral}")
    log_step(f"RHS Integral ∫ g(x) dx: {rhs_integral}")
    
    # 5. Formulate implicit solution: ∫ 1/h(y) dy = ∫ g(x) dx + C
    
    # We return a string to denote an implicit solution (since we cannot explicitly solve for y)
    return f"Implicit Solution: {lhs_integral} = ({rhs_integral}+C)"

# -----------------------------------------------

def ODEsolver(ode_expr: Expr, x_var: str = "x", y_var: str = "y") -> str:
    """
    Classifies and attempts to solve a first-order ODE given in the implicit form LHS = 0.
    """
    dy_dx_marker = DyDx(y_var, x_var)
    
    reset_log()
    log_step(f"Starting ODE solver for ODE: {ode_expr} = 0")
    
    # 1. NORMALIZATION: Convert F(y', x, y) = 0 to M + N*y' = 0 and y' = f(x, y)
    M, N, f_xy = normalize_ode(ode_expr, dy_dx_marker, x_var)
    
    if M is None:
        return "Error: Normalization failed. Could not isolate the y' term."
        
    log_step(f"Normalized explicit form: dy/dx = {f_xy}")
    
    # 2. CLASSIFICATION
    ode_type = classify_first_order(f_xy, x_var, y_var)
    log_step(f"ODE classified as: {ode_type}")

    # 3. SOLUTION STRATEGY (Now supports Separable-f(x) and Separable-g(x)h(y))
    if ode_type == "Separable-f(x)":
        solution = solve_separable_fx(f_xy, x_var)
        return f"Solution y(x) = {solution}"
    
    # NEW SOLVER IMPLEMENTATION CHECK
    if ode_type == "Separable-g(x)h(y)":
        solution = solve_separable_gxh(f_xy, x_var, y_var)
        return solution # Returns the explicit string for implicit solution
    
    # 4. FALLBACK for non-implemented types
    return f"Classification: {ode_type}. Solution strategy for this type is not yet implemented."


# ------------------------------------------------------------
# ODE TEST HARNESS (Using full ODE syntax)
# ------------------------------------------------------------
if __name__ == "__main__":
    print("\n=== ODE Solver and Classifier Test Harness ===\n")

    x = Var("x")
    y = Var("y")
    dy_dx = DyDx("y", "x") # d(y)/d(x)
    
    tests = [
        
        # --- Type: Separable-f(x) (Already Solved) ---
        (
            "ODE 1: Separable f(x) (y' + M(x) = 0)",
            # dy/dx + 3x^2 + e^(2x) = 0
            Add(dy_dx, Add(Mul(Const(3), Pow(x, Const(2))), Exp(Mul(Const(2), x)))), 
            "Separable-f(x)"
        ),
        
        # --- Type: Separable-g(x)h(y) (NOW SOLVABLE) ---
        (
            "ODE 2: Separable-g(x)h(y) (Multiplicative)",
            # dy/dx - x*y = 0  -> dy/dx = x*y  (g(x)=x, h(y)=y)
            Sub(dy_dx, Mul(x, y)), 
            "Separable-g(x)h(y)"
        ),
        
        # --- Type: Homogeneous ---
        (
            "ODE 3: Homogeneous (y' = (x^2+y^2)/xy)",
            # x*y*dy/dx - x^2 - y^2 = 0
            Sub(Mul(Mul(x, y), dy_dx), Add(Pow(x, Const(2)), Pow(y, Const(2)))),
            "Homogeneous"
        ),
        
        # --- Type: Linear First-Order ---
        (
            "ODE 4: Linear First-Order (y' + P(x)y = Q(x))",
            # dy/dx + (1/x)y - cos(x) = 0
            Sub(Add(dy_dx, Div(y, x)), Cos(x)),
            "Linear" 
        ),
        
        # --- Type: General (The fallback type) ---
        (
            "ODE 5: General/Non-Separable (y' = x + y^2)",
            # dy/dx - x - y^2 = 0
            Sub(dy_dx, Add(x, Pow(y, Const(2)))),
            "General" 
        ),
    ]
    for name, ode_expr, expected_type in tests:
        print(f"========================================")
        print(f"▶ {name}")
        print(f"Input ODE: {ode_expr} = 0")
        
        # Decompose for display
        M, N, f_xy = normalize_ode(ode_expr, dy_dx, "x")
        
        # Run solver
        result = ODEsolver(ode_expr, x_var="x", y_var="y")
        
        print(f"Decomposition:")
        print(f"  M(x,y) = {M}")
        print(f"  N(x,y) = {N}")
        print(f"  y' = f(x,y) = {f_xy}")
        
        print(f"Solver Output: {result}")
        print(f"Total rewrite steps logged: {get_step_counter()}")
        print(f"Log written to: {LOG_FILE}\n")