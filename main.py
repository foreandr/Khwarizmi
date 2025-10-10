# ------------------------------------------------------------
# Symbolic System Demo
# ------------------------------------------------------------
from core.expr import *
from core.rules import get_rule
from core.proof_kernel import ProofKernel
from core.logger import export_latex
from core.latex_export import write_and_compile_latex  # ✅ new import
import core.axioms_vector_space


def main():
    kernel = ProofKernel()

    expr = ScalarMul(Const(1), Add(Var("u"), Var("v")))

    # Apply distributivity
    rule = get_rule("VS_Distrib_Vector")
    expr = kernel.apply_rule(expr, rule.apply, rule.name, rule.description)

    # Apply scalar identity recursively
    id_rule = get_rule("VS_Scalar_Id")
    expr = kernel.apply_rule(expr, id_rule.apply, id_rule.name, id_rule.description)

    # Log proof
    for step in kernel.get_trace():
        print(f"{step.before}  -->[{step.rule}]-->  {step.after}")

    tex = export_latex(kernel.get_trace())
    write_and_compile_latex(tex, "proof.pdf")


if __name__ == "__main__":
    main()
