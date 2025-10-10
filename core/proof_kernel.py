# ------------------------------------------------------------
# Proof Kernel — logs each rule application formally
# ------------------------------------------------------------
from dataclasses import dataclass
from typing import List, Callable
from .expr import Expr

@dataclass
class ProofStep:
    before: Expr
    after: Expr
    rule: str
    justification: str
    status: str = "ok"  # "ok" or "error"


class ProofKernel:
    def __init__(self):
        self.trace: List[ProofStep] = []

    def apply_rule(self, expr: Expr, rule_fn: Callable[[Expr], Expr],
                   rule_name: str, justification: str):
        """
        Try to apply a rule (recursively). 
        If it fails, log a warning step instead of raising.
        """
        try:
            # Try top-level application first
            new_expr = rule_fn(expr)
            if new_expr is not None and str(new_expr) != str(expr):
                step = ProofStep(expr, new_expr, rule_name, justification, "ok")
                self.trace.append(step)
                return new_expr

            # Otherwise, recurse into children
            if hasattr(expr, "__dict__"):
                new_fields = {}
                changed = False
                for k, v in expr.__dict__.items():
                    if isinstance(v, Expr):
                        new_v = self.apply_rule(v, rule_fn, rule_name, justification)
                        if str(new_v) != str(v):
                            changed = True
                        new_fields[k] = new_v
                    else:
                        new_fields[k] = v
                if changed:
                    new_expr = expr.__class__(**new_fields)
                    step = ProofStep(expr, new_expr, rule_name, justification, "ok")
                    self.trace.append(step)
                    return new_expr

            # If nothing matched at any depth
            self.trace.append(ProofStep(expr, expr, rule_name,
                                        f"Rule not applicable to {expr}", "error"))
            return expr

        except Exception as e:
            # Hard error (like malformed structure)
            self.trace.append(ProofStep(expr, expr, rule_name,
                                        f"Exception during rule: {e}", "error"))
            return expr

    def get_trace(self):
        return self.trace
