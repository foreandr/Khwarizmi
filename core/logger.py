# ------------------------------------------------------------
# Logging and LaTeX Export
# ------------------------------------------------------------
from .proof_kernel import ProofStep

def export_latex(steps: list[ProofStep]) -> str:
    """
    Convert proof steps into a valid LaTeX align* environment.
    Error steps are shown in red text.
    """
    lines = [
        r"\usepackage{xcolor}",
        r"\begin{align*}"
    ]

    for s in steps:
        before = s.before.to_latex()
        after = s.after.to_latex()
        rule = s.rule.replace("_", r"\_")

        if s.status == "ok":
            justification = s.justification.replace("_", r"\_")
            lines.append(
                f"{before} &\\overset{{\\text{{{rule}}}}}{{=}} {after} "
                f"& \\text{{({justification})}} \\\\"
            )
        else:
            justification = s.justification.replace("_", r"\_")
            lines.append(
                f"\\textcolor{{red}}{{\\textbf{{Failed: {rule}}}}} "
                f"& \\textcolor{{red}}{{\\textit{{{justification}}}}} \\\\"
            )

    lines.append(r"\end{align*}")
    return "\n".join(lines)
