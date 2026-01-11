import javalang
from javalang.ast import walk_tree
from javalang.tree import StatementExpression, MethodInvocation
from ..thresholds import SMELL_CATEGORY_WEIGHTS

# methods on ResultSet whose return value must be checked
_METHODS = {"next", "previous", "first", "last"}

def detect_result_set_check(node, source_lines, filepath, filename):
    # Only top‐level statement expressions
    if not isinstance(node, StatementExpression):
        return None

    # Must be a method invocation
    mi = node.expression
    if not isinstance(mi, MethodInvocation):
        return None

    # Method name must be one of the RESULTSET navigation calls
    if mi.member not in _METHODS:
        return None

    line = node.position.line if node.position else 1
    return [{
        "codeSmellType": "ResultSet Navigation Not Checked",
        "filename":      filename,
        "filepath":      filepath,
        "startline":     line,
        "endline":       line,
        "code":          "RSC",
        "category":      "Best Practices",
        "weight":        SMELL_CATEGORY_WEIGHTS.get("Result Set Check", 2)
    }]
