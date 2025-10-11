# tests/test_vector_space.py
# ------------------------------------------------------------
# Vector Space Axiom Test Cases
# ------------------------------------------------------------
from core.expr import *
from core.proof_kernel import ProofKernel
from core.logger import export_latex
from core.latex_export import write_and_compile_latex
from core.solver import simplify 

# Ensure axioms are loaded (even if unused directly)
import core.axioms_vector_space 


def run_test_scalar_identity():
    """
    Test case 1: Prove 1 · (u + v) = u + v
    """
    print("\n=============================================")
    print("= TEST 1: Scalar Identity Proof (1·(u+v))   =")
    print("=============================================")

    kernel = ProofKernel()
    expr = ScalarMul(Const(1), Add(Var("u"), Var("v")))
    
    print(f"Starting expression: {expr}")
    print("Applying simplification strategy...")
    final_expr, made_change = simplify(expr, kernel)
    
    print(f"\nFinal simplified expression: {final_expr}")
    
    goal_str = f"{expr} = {final_expr}" 
    tex = export_latex(kernel.get_trace(), goal=goal_str)
    write_and_compile_latex(tex, "test_1_scalar_identity_proof.pdf")

    assert str(final_expr) == "(u + v)", "Test 1 Failed: Expected (u + v)"
    print("Test 1 Assertion: Passed.")


def run_test_scalar_associativity():
    """
    Test case 2: Prove 1 · (1 · u) = u
    """
    print("\n=============================================")
    print("= TEST 2: Scalar Associativity Proof (1·(1·u))=")
    print("=============================================")

    kernel = ProofKernel()
    expr = ScalarMul(Const(1), ScalarMul(Const(1), Var("u")))
    
    print(f"Starting expression: {expr}")
    print("Applying simplification strategy...")
    final_expr, made_change = simplify(expr, kernel)
    
    print(f"\nFinal simplified expression: {final_expr}")
    
    goal_str = f"{expr} = {final_expr}" 
    tex = export_latex(kernel.get_trace(), goal=goal_str)
    write_and_compile_latex(tex, "test_2_scalar_associativity_proof.pdf")

    assert str(final_expr) == "u", "Test 2 Failed: Expected u"
    print("Test 2 Assertion: Passed.")


def run_test_complex_inverse():
    """
    Test case 3: Prove 2 · (u + 0) + (-1) · u = u
    (This is the complex simplification that was causing loops)
    """
    print("\n=============================================")
    print("= TEST 3: Complex Inverse Proof             =")
    print("=============================================")

    kernel = ProofKernel()

    # Initial expression: 2 · (u + 0) + (-1) · u 
    expr = Add(
        ScalarMul(Const(2), Add(Var("u"), Const(0))),
        ScalarMul(Const(-1), Var("u"))
    )
    
    print(f"Starting expression: {expr}")
    print("Applying simplification strategy...")
    final_expr, made_change = simplify(expr, kernel)
    
    print(f"\nFinal simplified expression: {final_expr}")
    
    goal_str = f"{expr} = {final_expr}" 
    tex = export_latex(kernel.get_trace(), goal=goal_str)
    write_and_compile_latex(tex, "test_3_complex_inverse_proof.pdf")

    # The expected result is: u.
    assert str(final_expr) == "u", "Test 3 Failed: Expected u"
    print("Test 3 Assertion: Passed.")


def run_test_additive_inverse():
    """
    Test case 4: Prove u + (-1) · u = 0
    Specifically designed to use VS_Add_Inv.
    """
    print("\n=============================================")
    print("= TEST 4: Pure Additive Inverse Proof       =")
    print("=============================================")

    kernel = ProofKernel()

    # Initial expression: u + (-1) · u 
    expr = Add(
        Var("u"),
        ScalarMul(Const(-1), Var("u"))
    )
    
    print(f"Starting expression: {expr}")
    print("Applying simplification strategy...")
    final_expr, made_change = simplify(expr, kernel)
    
    print(f"\nFinal simplified expression: {final_expr}")
    
    goal_str = f"{expr} = {final_expr}" 
    tex = export_latex(kernel.get_trace(), goal=goal_str)
    write_and_compile_latex(tex, "test_4_additive_inverse_proof.pdf")

    # The expected result is: 0.
    assert str(final_expr) == "0", "Test 4 Failed: Expected 0"
    print("Test 4 Assertion: Passed.")


def run_all_tests():
    run_test_scalar_identity()
    run_test_scalar_associativity()
    run_test_complex_inverse()
    # 🌟 NEW TEST ADDED:
    run_test_additive_inverse()


if __name__ == "__main__":
    run_all_tests()