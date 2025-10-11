# main.py
# ------------------------------------------------------------
# Symbolic System Demo
# ------------------------------------------------------------
from core.expr import *
from core.rules import get_rule
from core.proof_kernel import ProofKernel
from core.logger import export_latex
from core.latex_export import write_and_compile_latex
from core.solver import simplify 
import core.axioms_vector_space # Ensures rules are registered

def main():
    kernel = ProofKernel()

    # Initial expression: 1 · (u + v)
    expr = ScalarMul(Const(1), Add(Var("u"), Var("v")))
    
    print(f"Starting expression: {expr}")
    
    # Use the automatic simplification strategy
    print("Applying simplification strategy...")
    final_expr, made_change = simplify(expr, kernel)
    
    print(f"\nFinal simplified expression: {final_expr}")

    # Log proof
    print("\n--- Proof Trace (Successful Steps Only) ---")
    if kernel.get_trace():
        # Only print 'ok' steps for the clean proof
        for step in [s for s in kernel.get_trace() if s.status == "ok"]:
            print(f"{step.before}  -->[{step.rule}]-->  {step.after} (Status: {step.status})")
    else:
        print("No steps were taken.")
    print("------------------------------------------\n")

    # The goal reflects the simplification result
    goal_str = f"{expr} = {final_expr}" 
    tex = export_latex(kernel.get_trace(), goal=goal_str)
    
    # FIX: Pass only the desired filename "proof.pdf". latex_export handles the 'pdf_folder' part.
    write_and_compile_latex(tex, "proof.pdf") 


if __name__ == "__main__":
    main()