# latex_export.py
# ------------------------------------------------------------
# LaTeX Export Utility (robust wrapper)
# - If the incoming tex_content already contains a preamble (\documentclass or \begin{document})
#   we write it as-is and compile.
# - Otherwise we wrap it in a minimal preamble and compile.
# ------------------------------------------------------------
import subprocess
import shutil
from pathlib import Path
import time


def write_and_compile_latex(tex_content: str, output_pdf: str = "proof.pdf") -> bool:
    """Write LaTeX to file and compile it to a PDF.
    Returns True on success, False on failure.
    """
    start = time.time()
    tex_file = Path("proof.tex")

    # detect whether tex_content already includes a full LaTeX document
    content_has_preamble = (
        r"\documentclass" in tex_content or r"\begin{document}" in tex_content
    )

    if content_has_preamble:
        full_doc = tex_content
    else:
        # wrap fragment in a small preamble
        full_doc = (
            r"\documentclass[12pt]{article}" "\n"
            r"\usepackage{amsmath}" "\n"
            r"\usepackage{xcolor}" "\n"
            r"\usepackage[margin=1in]{geometry}" "\n"
            r"\setlength{\parindent}{0pt}" "\n"
            r"\setlength{\parskip}{0.5em}" "\n"
            r"\begin{document}" "\n"
            + tex_content
            + "\n" r"\end{document}"
        )

    tex_file.write_text(full_doc, encoding="utf-8")
    print(f"[LaTeX Write] Completed in {time.time() - start:.3f} s (preamble included: {content_has_preamble})")

    # --- find pdflatex executable ---
    pdflatex_path = shutil.which("pdflatex")
    if pdflatex_path is None:
        # fallback path used previously in your environment
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
        # move result to requested output filename
        pdf_path.replace(Path(output_pdf))
        print(f"✅ PDF generated: {output_pdf}")
        print(f"[LaTeX Compile] Completed in {compile_time:.3f} s")
        return True
    else:
        print("⚠️  PDF compilation failed.\n--- STDOUT ---")
        print(result.stdout)
        print("--- STDERR ---")
        print(result.stderr)
        print(f"[LaTeX Compile] Attempted in {compile_time:.3f} s")
        return False
