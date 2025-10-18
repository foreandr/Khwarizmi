# ODEsolver.py (Adding Explicit Separable-g(x)h(y) solution for log(|y|) case)

from rules import Var, Const, Add, Mul, Pow, Exp, Log, Sin, Cos, Sub, Div, Neg, Expr, Abs
from integration import integrate
from ODEclassifier import classify_first_order # We now import the classifier
from utils import is_independent_of
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
    
    if isinstance(expr, DyDx):
        return [expr]
    if not isinstance(expr, (Add, Sub, Neg)):
        return [expr]
    
    if isinstance(expr, Add):
        terms.extend(flatten_ode_terms(expr.left))
        terms.extend(flatten_ode_terms(expr.right))
    elif isinstance(expr, Sub):
        terms.extend(flatten_ode_terms(expr.left))
        
        right_negated = Neg(expr.right)
        right_negated = rewrite(right_negated, simplification_rules())
        right_negated = evaluate_constants(right_negated)
        terms.append(right_negated)
    elif isinstance(expr, Neg):
        arg = expr.arg
        if isinstance(arg, Add):
            # -(A+B) = (-A) + (-B)
            terms.extend(flatten_ode_terms(Neg(arg.left)))
            terms.extend(flatten_ode_terms(Neg(arg.right)))
        elif isinstance(arg, Sub):
            # -(A-B) = (-A) + B
            terms.extend(flatten_ode_terms(Neg(arg.left)))
            terms.extend(flatten_ode_terms(arg.right))
        else:
            terms.append(expr)

    return terms


def normalize_ode(ode_expr: Expr, dy_dx_marker: DyDx, x_var: str) -> tuple[Expr, Expr, Expr]:
    """
    Normalizes F(y', x, y) = 0 into M(x,y) + N(x,y)*y' = 0 and y' = f(x,y).
    Returns: (M, N, f_xy)
    """
    log_step(f"Normalizing ODE: solving for {dy_dx_marker}")
    
    flat_terms = flatten_ode_terms(ode_expr)

    n_y_prime_term = None
    m_terms = []

    for term in flat_terms:
        is_derivative_term = False
        
        if term == dy_dx_marker:
            n_y_prime_term = term
            is_derivative_term = True
        elif isinstance(term, Mul) and (term.left == dy_dx_marker or term.right == dy_dx_marker):
            n_y_prime_term = term
            is_derivative_term = True
                
        if not is_derivative_term:
            m_terms.append(term)
        
    if n_y_prime_term == dy_dx_marker:
        N = Const(1)
    elif isinstance(n_y_prime_term, Mul):
        N = n_y_prime_term.right if n_y_prime_term.left == dy_dx_marker else n_y_prime_term.left
    else:
        log_step("Normalization failed: Could not isolate N*y' term.")
        return None, None, ode_expr
        

    M = m_terms[0] if m_terms else Const(0)
    for i in range(1, len(m_terms)):
        M = Add(M, m_terms[i])
        
    M = rewrite(M, simplification_rules()); M = evaluate_constants(M)
    N = rewrite(N, simplification_rules()); N = evaluate_constants(N)

    f_xy = Div(Neg(M), N)
    f_xy = rewrite(f_xy, simplification_rules()); f_xy = evaluate_constants(f_xy)

    log_step(f"Decomposition: M={M}, N={N}")
    log_step(f"Normalized RHS f(x,y): {f_xy}")
    return M, N, f_xy


def solve_separable_fx(f_x: Expr, x_var: str = "x") -> Expr:
    """Solves dy/dx = f(x) by direct integration (y = ∫ f(x) dx + C)."""
    log_step(f"Solving ODE using: Direct Integration (∫ f(x) dx + C)")
    
    integral_result = integrate(f_x, x_var, reset=True)
    
    C = Var("C") 
    solution = Add(integral_result, C)
    return solution

def solve_separable_gxh(f_xy: Expr, x_var: str = "x", y_var: str = "y") -> str:
    """Solves dy/dx = g(x)h(y) by separating variables (∫ 1/h(y) dy = ∫ g(x) dx + C)."""
    log_step(f"Solving ODE using: Separation of Variables (∫ 1/h(y) dy = ∫ g(x) dx + C)")
    
    x = Var(x_var); y = Var(y_var); C = Var("C")
    g_x, h_y = None, None
    
    if isinstance(f_xy, (Mul, Div)):
        if is_independent_of(f_xy.left, y) and is_independent_of(f_xy.right, x):
            g_x, h_y = f_xy.left, f_xy.right
        elif is_independent_of(f_xy.right, y) and is_independent_of(f_xy.left, x):
            g_x, h_y = f_xy.right, f_xy.left
        
    if g_x is None or h_y is None:
         return "Classification: Separable-g(x)h(y). Error in g(x)h(y) decomposition."

    # 1. Integrate LHS (in terms of y)
    one_over_h_y = Div(Const(1), h_y)
    one_over_h_y = rewrite(one_over_h_y, simplification_rules()); one_over_h_y = evaluate_constants(one_over_h_y)
    
    lhs_integral = integrate(one_over_h_y, y_var, reset=True)
    
    # 2. Integrate RHS (in terms of x)
    rhs_integral = integrate(g_x, x_var, reset=True)
    
    log_step(f"g(x) = {g_x}, h(y) = {h_y}")
    log_step(f"LHS Integral ∫ (1/h) dy: {lhs_integral}")
    log_step(f"RHS Integral ∫ g(x) dx: {rhs_integral}")
    
    # 3. Formulate solution: ∫ 1/h(y) dy = ∫ g(x) dx + C

    # === NEW LOGIC: Check for log(|y|) on LHS to solve explicitly ===
    A = Var("A") # New arbitrary constant A = +/- e^C

    # Check for Log(y) or Log(Abs(y))
    is_log_y = False
    if isinstance(lhs_integral, Log):
        # Allow Log(y) or Log(Abs(y)) as the argument. The Abs() is just for notation here.
        if lhs_integral.arg == y or lhs_integral.arg == Abs(y):
            is_log_y = True

    if is_log_y:
        log_step("LHS is log(|y|). Solving explicitly: y = A * exp(∫ g(x) dx).")
        
        # Solution is y = A * e^(rhs_integral)
        solution = Mul(A, Exp(rhs_integral))

        solution = rewrite(solution, simplification_rules()); solution = evaluate_constants(solution)
        
        return f"Solution y(x) = {solution}"
    # =================================================================
    
    # Fallback to implicit solution
    return f"Implicit Solution: {lhs_integral} = ({rhs_integral}+C)"

# --- Linear First-Order Solver (Unchanged) ---

def solve_linear_first_order(f_xy: Expr, x_var: str = "x", y_var: str = "y") -> str:
    """
    Solves y' = f(x,y) by transforming to y' + P(x)y = Q(x) and using an Integrating Factor.
    """
    log_step("Solving ODE using: Integrating Factor method.")
    x = Var(x_var); y = Var(y_var); C = Var("C")

    # 1. Decompose f_xy = Q(x) + (-P(x)y term)
    terms = flatten_ode_terms(f_xy) 

    Q_x_terms = []
    P_x_y_term = Const(0)
    
    for term in terms:
        if is_independent_of(term, y):
            Q_x_terms.append(term)
        else:
            P_x_y_term = Add(P_x_y_term, term)
            
    Q_x = Q_x_terms[0] if Q_x_terms else Const(0)
    for i in range(1, len(Q_x_terms)):
        Q_x = Add(Q_x, Q_x_terms[i])
    Q_x = rewrite(Q_x, simplification_rules()); Q_x = evaluate_constants(Q_x)
    
    neg_P_x = Div(P_x_y_term, y)
    neg_P_x = rewrite(neg_P_x, simplification_rules()); neg_P_x = evaluate_constants(neg_P_x)
    
    P_x = Neg(neg_P_x)
    P_x = rewrite(P_x, simplification_rules()); P_x = evaluate_constants(P_x)
    
    log_step(f"Decomposition: P(x) = {P_x}, Q(x) = {Q_x}")

    # 2. Calculate Integral of P(x): I_P = ∫ P(x) dx
    I_P = integrate(P_x, x_var, reset=True)

    # 3. Calculate Integrating Factor: mu = e^(I_P)
    mu = Exp(I_P)
    mu = rewrite(mu, simplification_rules()); mu = evaluate_constants(mu)
    log_step(f"Integrating Factor: mu = {mu}")
    
    # 4. Calculate Integral of mu*Q(x): I_muQ = ∫ mu*Q(x) dx
    mu_Q = Mul(mu, Q_x)
    mu_Q = rewrite(mu_Q, simplification_rules()); mu_Q = evaluate_constants(mu_Q)
    
    I_muQ = integrate(mu_Q, x_var, reset=True)
    log_step(f"Integral of mu*Q(x): I_muQ = {I_muQ}")

    # 5. Final Solution: y = (1/mu) * (I_muQ + C)
    inv_mu = Div(Const(1), mu)
    solution_core = Add(I_muQ, C)
    solution = Mul(inv_mu, solution_core)

    solution = rewrite(solution, simplification_rules()); solution = evaluate_constants(solution)
    
    return f"Solution y(x) = {solution}"

# -----------------------------------------------

def ODEsolver(ode_expr: Expr, x_var: str = "x", y_var: str = "y") -> str:
    """
    Classifies and attempts to solve a first-order ODE given in the implicit form LHS = 0.
    """
    dy_dx_marker = DyDx(y_var, x_var)
    
    reset_log()
    log_step(f"Starting ODE solver for ODE: {ode_expr} = 0")
    
    M, N, f_xy = normalize_ode(ode_expr, dy_dx_marker, x_var)
    
    if M is None:
        return "Error: Normalization failed. Could not isolate the y' term."
        
    log_step(f"Normalized explicit form: dy/dx = {f_xy}")
    
    ode_type = classify_first_order(f_xy, x_var, y_var)
    log_step(f"ODE classified as: {ode_type}")

    if ode_type == "Separable-f(x)":
        return f"Solution y(x) = {solve_separable_fx(f_xy, x_var)}"
    
    if ode_type == "Separable-g(x)h(y)":
        return solve_separable_gxh(f_xy, x_var, y_var)
        
    if ode_type == "Linear":
        return solve_linear_first_order(f_xy, x_var, y_var)
    
    return f"Classification: {ode_type}. Solution strategy for this type is not yet implemented."


# ------------------------------------------------------------
# ODE TEST HARNESS (Unchanged)
# ------------------------------------------------------------
if __name__ == "__main__":
    print("\n=== ODE Solver and Classifier Test Harness ===\n")

    x = Var("x")
    y = Var("y")
    dy_dx = DyDx("y", "x")
    
    tests = [
        
        ("ODE 1: Separable f(x) (y' + M(x) = 0)",
            Add(dy_dx, Add(Mul(Const(3), Pow(x, Const(2))), Exp(Mul(Const(2), x)))), 
            "Separable-f(x)"
        ),
        
        ("ODE 2: Separable-g(x)h(y) (Multiplicative)",
            Sub(dy_dx, Mul(x, y)), 
            "Separable-g(x)h(y)"
        ),
        
        ("ODE 3: Homogeneous (y' = (x^2+y^2)/xy)",
            Sub(Mul(Mul(x, y), dy_dx), Add(Pow(x, Const(2)), Pow(y, Const(2)))),
            "Homogeneous"
        ),
        
        ("ODE 4: Linear First-Order (y' + P(x)y = Q(x))",
            Sub(Add(dy_dx, Div(y, x)), Cos(x)),
            "Linear" 
        ),
        
        ("ODE 5: General/Non-Separable (y' = x + y^2)",
            Sub(dy_dx, Add(x, Pow(y, Const(2)))),
            "General" 
        ),
    ]
    for name, ode_expr, expected_type in tests:
        print(f"========================================")
        print(f"▶ {name}")
        print(f"Input ODE: {ode_expr} = 0")
        
        M, N, f_xy = normalize_ode(ode_expr, dy_dx, "x")
        
        result = ODEsolver(ode_expr, x_var="x", y_var="y")
        
        print(f"Decomposition:")
        print(f"  M(x,y) = {M}")
        print(f"  N(x,y) = {N}")
        print(f"  y' = f(x,y) = {f_xy}")
        
        print(f"Solver Output: {result}")
        print(f"Total rewrite steps logged: {get_step_counter()}")
        print(f"Log written to: {LOG_FILE}\n")