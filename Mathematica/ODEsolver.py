# ============================================================
# ODEsolver.py — Full version with linear fix and homogeneous support
# ============================================================

from rules import Var, Const, Add, Mul, Pow, Exp, Log, Sin, Cos, Sub, Div, Neg, Expr, Abs
from integration import integrate
from ODEclassifier import classify_first_order
from utils import is_independent_of
from logger import reset_log, log_step, get_step_counter, LOG_FILE
from simplification import rewrite, simplification_rules, evaluate_constants

# ============================================================
# dy/dx representation
# ============================================================

class DyDx(Expr):
    """Represents the first derivative dy/dx."""
    def __init__(self, var: str = "y", wrt: str = "x"):
        self.var = Var(var)
        self.wrt = Var(wrt)
    def children(self): return [self.var, self.wrt]
    def __repr__(self): return f"d{self.var}/d{self.wrt}"
    def __eq__(self, other):
        return isinstance(other, DyDx) and repr(self) == repr(other)

# ============================================================
# utility: flatten additive terms
# ============================================================

def flatten_ode_terms(expr):
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
        right_neg = Neg(expr.right)
        right_neg = rewrite(right_neg, simplification_rules())
        right_neg = evaluate_constants(right_neg)
        terms.append(right_neg)
    elif isinstance(expr, Neg):
        arg = expr.arg
        if isinstance(arg, Add):
            terms.extend(flatten_ode_terms(Neg(arg.left)))
            terms.extend(flatten_ode_terms(Neg(arg.right)))
        elif isinstance(arg, Sub):
            terms.extend(flatten_ode_terms(Neg(arg.left)))
            terms.extend(flatten_ode_terms(arg.right))
        else:
            terms.append(expr)
    return terms

# ============================================================
# normalization
# ============================================================

def normalize_ode(ode_expr: Expr, dy_dx_marker: DyDx, x_var: str) -> tuple[Expr, Expr, Expr]:
    log_step(f"Normalizing ODE: solving for {dy_dx_marker}")
    flat_terms = flatten_ode_terms(ode_expr)
    n_yprime = None
    m_terms = []
    for term in flat_terms:
        if term == dy_dx_marker:
            n_yprime = term
        elif isinstance(term, Mul) and (term.left == dy_dx_marker or term.right == dy_dx_marker):
            n_yprime = term
        else:
            m_terms.append(term)
    if n_yprime == dy_dx_marker:
        N = Const(1)
    elif isinstance(n_yprime, Mul):
        N = n_yprime.right if n_yprime.left == dy_dx_marker else n_yprime.left
    else:
        log_step("Normalization failed: cannot isolate dy/dx term")
        return None, None, ode_expr
    M = m_terms[0] if m_terms else Const(0)
    for t in m_terms[1:]:
        M = Add(M, t)
    M = rewrite(M, simplification_rules()); M = evaluate_constants(M)
    N = rewrite(N, simplification_rules()); N = evaluate_constants(N)
    f_xy = Div(Neg(M), N)
    f_xy = rewrite(f_xy, simplification_rules()); f_xy = evaluate_constants(f_xy)
    log_step(f"Decomposition: M={M}, N={N}")
    log_step(f"Normalized RHS f(x,y): {f_xy}")
    return M, N, f_xy

# ============================================================
# separable f(x)
# ============================================================

def solve_separable_fx(f_x: Expr, x_var="x") -> Expr:
    log_step("Solving ODE using: Direct Integration (∫f(x)dx + C)")
    res = integrate(f_x, x_var, reset=True)
    return Add(res, Var("C"))

# ============================================================
# separable g(x)h(y)
# ============================================================

def solve_separable_gxh(f_xy: Expr, x_var="x", y_var="y") -> str:
    log_step("Solving ODE using: Separation of Variables (∫1/h dy = ∫g dx + C)")
    x, y, C = Var(x_var), Var(y_var), Var("C")
    g_x = h_y = None
    if isinstance(f_xy, (Mul, Div)):
        if is_independent_of(f_xy.left, y) and is_independent_of(f_xy.right, x):
            g_x, h_y = f_xy.left, f_xy.right
        elif is_independent_of(f_xy.right, y) and is_independent_of(f_xy.left, x):
            g_x, h_y = f_xy.right, f_xy.left
    if g_x is None or h_y is None:
        return "Classification: Separable-g(x)h(y). Error in decomposition."
    one_over_h = Div(Const(1), h_y)
    one_over_h = rewrite(one_over_h, simplification_rules()); one_over_h = evaluate_constants(one_over_h)
    lhs = integrate(one_over_h, y_var, reset=True)
    rhs = integrate(g_x, x_var, reset=True)
    log_step(f"g(x)={g_x}, h(y)={h_y}")
    log_step(f"LHS ∫(1/h)dy={lhs}")
    log_step(f"RHS ∫g(x)dx={rhs}")
    A = Var("A")
    if isinstance(lhs, Log) and (lhs.arg == y or lhs.arg == Abs(y)):
        log_step("Detected log|y| ⇒ explicit exponential solution")
        sol = Mul(A, Exp(rhs))
        sol = rewrite(sol, simplification_rules()); sol = evaluate_constants(sol)
        return f"Solution y(x) = {sol}"
    return f"Implicit Solution: {lhs} = ({rhs}+C)"

# ============================================================
# linear ODE solver — FIXED SIMPLIFICATION
# ============================================================

def solve_linear_first_order(f_xy: Expr, x_var="x", y_var="y") -> str:
    log_step("Solving ODE using: Integrating Factor method")
    x, y, C = Var(x_var), Var(y_var), Var("C")
    terms = flatten_ode_terms(f_xy)
    Q_terms, P_term = [], Const(0)
    for t in terms:
        if is_independent_of(t, y):
            Q_terms.append(t)
        else:
            P_term = Add(P_term, t)
    Q_x = Q_terms[0] if Q_terms else Const(0)
    for q in Q_terms[1:]:
        Q_x = Add(Q_x, q)
    Q_x = rewrite(Q_x, simplification_rules()); Q_x = evaluate_constants(Q_x)

    # --- isolate and simplify P(x) completely ---
    neg_P_x = Div(P_term, y)
    for _ in range(3):
        neg_P_x = rewrite(neg_P_x, simplification_rules())
        neg_P_x = evaluate_constants(neg_P_x)

    P_x = Neg(neg_P_x)
    for _ in range(3):
        P_x = rewrite(P_x, simplification_rules())
        P_x = evaluate_constants(P_x)

    log_step(f"Decomposition: P(x)={P_x}, Q(x)={Q_x}")

    I_P = integrate(P_x, x_var, reset=True)
    mu = Exp(I_P)
    mu = rewrite(mu, simplification_rules()); mu = evaluate_constants(mu)
    log_step(f"Integrating Factor μ(x)={mu}")

    muQ = Mul(mu, Q_x)
    muQ = rewrite(muQ, simplification_rules()); muQ = evaluate_constants(muQ)
    I_muQ = integrate(muQ, x_var, reset=True)
    inv_mu = Div(Const(1), mu)
    sol = Mul(inv_mu, Add(I_muQ, C))
    sol = rewrite(sol, simplification_rules()); sol = evaluate_constants(sol)
    return f"Solution y(x) = {sol}"

# ============================================================
# homogeneous ODE solver (safe symbolic)
# ============================================================

def _substitute_y(expr: Expr, y_var: Var, new_expr: Expr) -> Expr:
    """Recursively substitute every occurrence of y with (v*x)."""
    if expr == y_var:
        return new_expr
    if not hasattr(expr, "children") or not expr.children():
        return expr
    args = [_substitute_y(c, y_var, new_expr) for c in expr.children()]
    return type(expr)(*args)

def solve_homogeneous(f_xy: Expr, x_var="x", y_var="y") -> str:
    log_step("Solving ODE using: Homogeneous Substitution (y=vx)")
    x, v, C = Var(x_var), Var("v"), Var("C")
    y = Var(y_var)
    # replace y→v*x structurally
    f_vx = _substitute_y(f_xy, y, Mul(v, x))
    f_vx = rewrite(f_vx, simplification_rules()); f_vx = evaluate_constants(f_vx)
    # dy/dx=v+x dv/dx ⇒ x dv/dx=f(vx)-v
    rhs = Sub(f_vx, v)
    rhs = rewrite(rhs, simplification_rules()); rhs = evaluate_constants(rhs)
    separable_rhs = Div(rhs, x)
    separable_rhs = rewrite(separable_rhs, simplification_rules()); separable_rhs = evaluate_constants(separable_rhs)
    log_step(f"Reduced to separable form: dv/dx = {separable_rhs}")
    lhs_int = integrate(Div(Const(1), Sub(f_vx, v)), "v", reset=True)
    rhs_int = integrate(Div(Const(1), x), "x", reset=True)
    log_step(f"LHS Integral (in v): {lhs_int}")
    log_step(f"RHS Integral (in x): {rhs_int}")
    return f"Implicit Solution: {lhs_int} = ({rhs_int}+C)"

# ============================================================
# master ODE solver
# ============================================================

def ODEsolver(ode_expr: Expr, x_var="x", y_var="y") -> str:
    dy = DyDx(y_var, x_var)
    reset_log()
    log_step(f"Starting ODE solver for ODE: {ode_expr}=0")
    M, N, f_xy = normalize_ode(ode_expr, dy, x_var)
    if M is None:
        return "Error: normalization failed"
    log_step(f"Normalized explicit form: dy/dx={f_xy}")
    t = classify_first_order(f_xy, x_var, y_var)
    log_step(f"ODE classified as: {t}")
    if t == "Separable-f(x)":
        return f"Solution y(x) = {solve_separable_fx(f_xy, x_var)}"
    if t == "Separable-g(x)h(y)":
        return solve_separable_gxh(f_xy, x_var, y_var)
    if t == "Linear":
        return solve_linear_first_order(f_xy, x_var, y_var)
    if t == "Homogeneous":
        return solve_homogeneous(f_xy, x_var, y_var)
    return f"Classification: {t}. Solution strategy for this type not yet implemented."

# ============================================================
# test harness
# ============================================================

if __name__ == "__main__":
    print("\n=== ODE Solver and Classifier Test Harness ===\n")
    x = Var("x"); y = Var("y"); dy = DyDx("y", "x")
    tests = [
        ("ODE 1: Separable f(x) (y' + M(x)=0)",
            Add(dy, Add(Mul(Const(3), Pow(x, Const(2))), Exp(Mul(Const(2), x)))),
            "Separable-f(x)"),
        ("ODE 2: Separable-g(x)h(y) (Multiplicative)",
            Sub(dy, Mul(x, y)),
            "Separable-g(x)h(y)"),
        ("ODE 3: Homogeneous (y'=(x^2+y^2)/xy)",
            Sub(Mul(Mul(x, y), dy), Add(Pow(x, Const(2)), Pow(y, Const(2)))),
            "Homogeneous"),
        ("ODE 4: Linear First-Order (y'+P(x)y=Q(x))",
            Sub(Add(dy, Div(y, x)), Cos(x)),
            "Linear"),
        ("ODE 5: General/Non-Separable (y'=x+y^2)",
            Sub(dy, Add(x, Pow(y, Const(2)))),
            "General"),
    ]
    for name, ode_expr, expected in tests:
        print("========================================")
        print(f"▶ {name}")
        print(f"Input ODE: {ode_expr}=0")
        M, N, f_xy = normalize_ode(ode_expr, dy, "x")
        res = ODEsolver(ode_expr, "x", "y")
        print("Decomposition:")
        print(f"  M(x,y)={M}")
        print(f"  N(x,y)={N}")
        print(f"  y' = f(x,y) = {f_xy}")
        print(f"Solver Output: {res}")
        print(f"Total rewrite steps logged: {get_step_counter()}")
        print(f"Log written to: {LOG_FILE}\n")
