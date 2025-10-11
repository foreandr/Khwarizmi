# core/proof_kernel.py
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
                   rule_name: str, justification: str) -> Expr:
        """
        Try to apply a rule (recursively).
        - Priority 1: Apply rule at the current node (top-level). If successful, return immediately.
        - Priority 2: If top-level fails, try applying the rule recursively to children.
        - If a child changes, reconstruct the current node and log the change propagation step.
        - If no change occurs at any depth, returns the original expression without logging a failure.
        
        Returns the (possibly) new expression.
        """
        original_expr = expr

        try:
            # 1. Try top-level application first
            new_expr = rule_fn(expr)
            if new_expr is not None and str(new_expr) != str(expr):
                # Log the top-level change
                step = ProofStep(expr, new_expr, rule_name, justification, "ok")
                self.trace.append(step)
                return new_expr  # SUCCESS: Return the new expression

            # 2. If top-level failed, try recursion
            if hasattr(expr, "__dict__"):
                new_fields = {}
                deep_change_occurred = False
                
                # Check if any child expression changed after applying the rule
                for k, v in expr.__dict__.items():
                    if isinstance(v, Expr):
                        # Recursive call: logs any deep changes and returns the new child expression
                        new_v = self.apply_rule(v, rule_fn, rule_name, justification)
                        
                        if str(new_v) != str(v):
                            deep_change_occurred = True
                        new_fields[k] = new_v
                    else:
                        new_fields[k] = v
                
                if deep_change_occurred:
                    # Construct the new parent expression from the modified children
                    result_expr = expr.__class__(**new_fields)

                    # Log the parent expression transformation.
                    step = ProofStep(original_expr, result_expr, rule_name, f"Recursive application of {rule_name}", "ok")
                    self.trace.append(step)
                    return result_expr
            
            # 3. If nothing matched at any depth (top-level or recursive)
            # CRITICAL FIX: DO NOT LOG failure steps here to prevent trace clutter.
            return expr

        except Exception as e:
            # Hard error (like malformed structure) - Keep this for severe issues
            self.trace.append(ProofStep(expr, expr, rule_name,
                                        f"Exception during rule: {e}", "error"))
            return expr

    def get_trace(self):
        return self.trace