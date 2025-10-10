# ------------------------------------------------------------
# Symbolic System Demo
# ------------------------------------------------------------
import subprocess
import shutil
import time
from pathlib import Path
from core.expr import *
from core.rules import get_rule
from core.proof_kernel import ProofKernel
from core.logger import export_latex
import core.axioms_vector_space  # registers rules


def write_and_compile_latex(tex_content: str, output_pdf: str = "proof.pdf"):
    """Write LaTeX to file and compile it to a PDF (MiKTeX-aware)."""
    start = time.time()
    tex_file = Path("proof.tex")

    full_doc = (
        r"\documentclass[12pt]{article}" "\n"
        r"\usepackage{amsmath}" "\n"
        r"\begin{document}" "\n"
        + tex_content + "\n"
        r"\end{document}"
    )
    tex_file.write_text(full_doc, encoding="utf-8")
    print(f"[LaTeX Write] Completed in {time.time() - start:.3f} s")

    # --- find pdflatex executable ---
    pdflatex_path = shutil.which("pdflatex")
    if pdflatex_path is None:
        pdflatex_path = r"C:\Users\forea\AppData\Local\Programs\MiKTeX\miktex\bin\x64\pdflatex.exe"

    print(f"Using LaTeX compiler: {pdflatex_path}")

    # --- compile ---
    start_compile = time.time()
    result = subprocess.run(
        [pdflatex_path, "-interaction=nonstopmode", tex_file.name],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    compile_time = time.time() - start_compile

    # --- check success ---
    pdf_path = tex_file.with_suffix(".pdf")
    if pdf_path.exists():
        pdf_path.replace(Path(output_pdf))
        print(f"✅ PDF generated: {output_pdf}")
        print(f"[LaTeX Compile] Completed in {compile_time:.3f} s")
    else:
        print("⚠️  PDF compilation failed.\n--- STDOUT ---")
        print(result.stdout)
        print("--- STDERR ---")
        print(result.stderr)
        print(f"[LaTeX Compile] Attempted in {compile_time:.3f} s")


def main():
    overall_start = time.time()

    kernel = ProofKernel()
    start_expr = time.time()
    expr = ScalarMul(Var("a"), Add(Var("u"), Var("v")))
    print(f"[Expression Build] Completed in {time.time() - start_expr:.3f} s")

    start_rule = time.time()
    rule = get_rule("VS_Distrib")
    kernel.apply_rule(expr, rule.apply, rule.name, rule.description)
    print(f"[Rule Application] Completed in {time.time() - start_rule:.3f} s")

    start_log = time.time()
    print("Proof trace:")
    for step in kernel.get_trace():
        print(f"{step.before}  -->[{step.rule}]-->  {step.after}")
    print(f"[Trace Print] Completed in {time.time() - start_log:.3f} s")

    start_tex = time.time()
    tex = export_latex(kernel.get_trace())
    print(f"[LaTeX Export] Completed in {time.time() - start_tex:.3f} s")

    write_and_compile_latex(tex, "proof.pdf")

    print(f"[Total Runtime] {time.time() - overall_start:.3f} s")


if __name__ == "__main__":
    main()
