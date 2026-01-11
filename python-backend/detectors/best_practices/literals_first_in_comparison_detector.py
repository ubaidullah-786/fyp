import javalang
from javalang.tree import MethodInvocation, Literal
from javalang.ast import walk_tree
from ..thresholds import SMELL_CATEGORY_WEIGHTS

# Methods where we want literals first
_COMPARISONS = {
    "equals",
    "equalsIgnoreCase",
    "compareTo",
    "compareToIgnoreCase",
    "contentEquals",
}

def _is_string_literal(expr):
    return isinstance(expr, Literal) and expr.value.startswith('"') and expr.value.endswith('"')

def detect_literals_first_in_comparison(node, source_lines, filepath, filename):
    if not isinstance(node, MethodInvocation):
        return None

    name = node.member
    if name not in _COMPARISONS:
        return None

    # must have exactly one argument
    args = node.arguments or []
    if len(args) != 1:
        return None

    qualifier = node.qualifier
    arg = args[0]

    if qualifier is None:
        return None

    # literal on the right, non-literal on the left
    if _is_string_literal(arg) and not _is_string_literal(qualifier):
        ln = node.position.line if node.position else 1
        return [{
            "codeSmellType": "Literal First In String Comparison",
            "filename":      filename,
            "filepath":      filepath,
            "startline":     ln,
            "endline":       ln,
            "code":          "LFSC",
            "category":      "Best Practices",
            "weight":        SMELL_CATEGORY_WEIGHTS.get("Literals First in Comparison", 1)
        }]

    return None
