# ------------------------------------------------------------
# Minimal Equational-Logic Proof Kernel
# ------------------------------------------------------------
from dataclasses import dataclass
from .expr import *

@dataclass
class ProofStep:
    before: Expr
    after: Expr
    rule: str
    justification: str

class ProofKernel:
    def __init__(self):
        self.steps: list[ProofStep] = []

    def apply_rule(self, expr: Expr, rule_fn, rule_name: str, justification: str) -> Expr:
        new_expr = rule_fn(expr)
        if new_expr is None:
            raise ValueError(f"Rule {rule_name} not applicable to {expr}")
        step = ProofStep(expr, new_expr, rule_name, justification)
        self.steps.append(step)
        return new_expr

    def get_trace(self):
        return self.steps
