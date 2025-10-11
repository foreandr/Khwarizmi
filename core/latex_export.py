# core/latex_export.py
# ------------------------------------------------------------
# LaTeX Export Utility
# ------------------------------------------------------------
import subprocess, shutil
from pathlib import Path
import time

PDF_OUTPUT_DIR = Path("pdf_folder")


def write_and_compile_latex(tex_content: str, output_pdf: str = "proof.pdf"):
    """Write LaTeX to file and compile it to a PDF (MiKTeX-aware)."""
    start = time.time()
    
    # 1. Setup paths
    PDF_OUTPUT_DIR.mkdir(exist_ok=True)
    # The temporary TeX file where the content is written
    tex_file = PDF_OUTPUT_DIR / "proof.tex"
    
    # The final intended path (relative to the project root, inside pdf_folder)
    final_pdf_path = PDF_OUTPUT_DIR / output_pdf 
    
    # 2. Write TeX content
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

    # 3. Find pdflatex executable
    pdflatex_path = shutil.which("pdflatex")
    if pdflatex_path is None:
        pdflatex_path = r"C:\Users\forea\AppData\Local\Programs\MiKTeX\miktex\bin\x64\pdflatex.exe"

    print(f"Using LaTeX compiler: {pdflatex_path}")

    # 4. Compile
    start_compile = time.time()
    result = subprocess.run(
        [
            pdflatex_path, 
            "-interaction=nonstopmode", 
            # Tell pdflatex where to find the source and write the output
            f"-output-directory={PDF_OUTPUT_DIR}", 
            tex_file.name # The name of the TeX file inside the directory
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        # Run from the base directory for path consistency
        cwd=Path.cwd() 
    )
    compile_time = time.time() - start_compile

    # 5. Check success and rename if necessary
    # The file created by pdflatex is always named 'proof.pdf' inside the output directory.
    generated_pdf_path = PDF_OUTPUT_DIR / tex_file.with_suffix(".pdf").name 
    
    if generated_pdf_path.exists():
        # Check if the desired output name is different (e.g., if you passed 'test.pdf')
        if generated_pdf_path.name != final_pdf_path.name:
            # We rename the 'proof.pdf' to the desired output name (e.g. 'test.pdf')
            generated_pdf_path.replace(final_pdf_path) 
            print(f"✅ PDF generated and renamed: {final_pdf_path}")
        else:
             print(f"✅ PDF generated: {generated_pdf_path}")
             
        print(f"[LaTeX Compile] Completed in {compile_time:.3f} s")
    else:
        print("⚠️  PDF compilation failed.\n--- STDOUT ---")
        print(result.stdout)
        print("--- STDERR ---")
        print(result.stderr)
        print(f"[LaTeX Compile] Attempted in {compile_time:.3f} s")