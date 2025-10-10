# ------------------------------------------------------------
# Rewrite Rules and Registry
# ------------------------------------------------------------
from dataclasses import dataclass
from typing import Callable, Dict, List, Union
from .expr import *

# ------------------------------------------------------------
# Rule class definition
# ------------------------------------------------------------

@dataclass
class Rule:
    name: str
    description: str
    apply: Callable[[Expr], Union[Expr, None]]


# ------------------------------------------------------------
# Global rule registry
# ------------------------------------------------------------
RULES: Dict[str, Rule] = {}


def register_rule(rule: Rule):
    """Register a symbolic rewrite rule."""
    RULES[rule.name] = rule


def get_rule(name: str) -> Rule:
    """Retrieve a rule by its name."""
    if name not in RULES:
        raise KeyError(f"Rule '{name}' not found.")
    return RULES[name]


def list_rules() -> List[str]:
    """Return all registered rule names."""
    return list(RULES.keys())
