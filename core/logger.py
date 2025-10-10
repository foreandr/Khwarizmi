# ------------------------------------------------------------
# Logging and LaTeX Export
# ------------------------------------------------------------
from .proof_kernel import ProofStep


def export_latex(steps: list[ProofStep]) -> str:
    """
    Convert proof steps into a valid LaTeX align* environment.

    Each step is displayed as:
    <math expr>  \overset{rule}{=}  <math expr>   (justification)
    """
    lines = [r"\begin{align*}"]

    for s in steps:
        # escape underscores to avoid LaTeX errors
        before = s.before.to_latex()
        after = s.after.to_latex()
        rule = s.rule.replace("_", r"\_")
        justification = s.justification.replace("_", r"\_")

        # each step rendered as one equation line
        lines.append(
            f"{before} &\\overset{{\\text{{{rule}}}}}{{=}} {after} "
            f"& \\text{{({justification})}} \\\\"
        )

    lines.append(r"\end{align*}")
    return "\n".join(lines)
