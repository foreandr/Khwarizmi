# ------------------------------------------------------------
# LaTeX Export Utility
# ------------------------------------------------------------
import subprocess, shutil
from pathlib import Path
import time

def write_and_compile_latex(tex_content: str, output_pdf: str = "proof.pdf"):
    """Write LaTeX to file and compile it to a PDF (MiKTeX-aware)."""
    start = time.time()
    
    # --- FIX: Use a unique .tex file name based on the PDF name ---
    temp_name = Path(output_pdf).with_suffix(".tex")
    
    tex_file = temp_name # Use the unique name here
    # -----------------------------------------------------------------

    full_doc = (
        r"\documentclass[12pt]{article}" "\n"
        r"\usepackage{amsmath}" "\n"
        r"\usepackage{xcolor}" "\n"
        r"\begin{document}" "\n"
        + tex_content + "\n"
        r"\end{document}"
    )
    tex_file.write_text(full_doc, encoding="utf-8")
    print(f"[LaTeX Write] Completed in {time.time() - start:.3f} s")

    # --- find pdflatex executable ---
    pdflatex_path = shutil.which("pdflatex")
    if pdflatex_path is None:
        # NOTE: Using the explicit path from your log as a fallback
        pdflatex_path = r"C:\Users\forea\AppData\Local\Programs\MiKTeX\miktex\bin\x64\pdflatex.exe"

    print(f"Using LaTeX compiler: {pdflatex_path}")

    # --- compile ---
    start_compile = time.time()
    result = subprocess.run(
        [pdflatex_path, "-interaction=nonstopmode", tex_file.name], # Compile the unique .tex file
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    compile_time = time.time() - start_compile

    # --- check success ---
    pdf_path = tex_file.with_suffix(".pdf") # This will be the unique .pdf file
    if pdf_path.exists():
        # Clean up the output by moving the unique PDF file to its final destination
        pdf_path.replace(Path("pdf_folder") / output_pdf) # Assuming the final directory is pdf_folder as per your log
        print(f"✅ PDF generated and renamed: pdf_folder\\{output_pdf}")
        print(f"[LaTeX Compile] Completed in {compile_time:.3f} s")
    else:
        print("⚠️  PDF compilation failed.\n--- STDOUT ---")
        print(result.stdout)
        print("--- STDERR ---")
        print(result.stderr)
        print(f"[LaTeX Compile] Attempted in {compile_time:.3f} s")