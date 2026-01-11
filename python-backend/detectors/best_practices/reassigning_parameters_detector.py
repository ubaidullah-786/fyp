import javalang
from javalang.ast import walk_tree
from javalang.tree import (
    MethodDeclaration,
    ConstructorDeclaration,
    StatementExpression,
    Assignment,
    MemberReference,
)
from ..thresholds import SMELL_CATEGORY_WEIGHTS

def detect_reassigning_parameters(node, source_lines, filepath, filename, **kwargs):
    if not isinstance(node, (MethodDeclaration, ConstructorDeclaration)):
        return None
    if not node.body:
        return None

    params = {p.name for p in node.parameters}
    if not params:
        return None

    reported = set()
    violations = []

    # Walk for StatementExpression nodes (they wrap assignments and have .position)
    for path, stmt in walk_tree(node.body):
        if not isinstance(stmt, StatementExpression):
            continue
        expr = stmt.expression
        if not isinstance(expr, Assignment):
            continue

        lhs = expr.expressionl
        # Only interested if LHS is one of our parameters
        if isinstance(lhs, MemberReference) and lhs.member in params:
            pname = lhs.member
            if pname in reported:
                continue
            reported.add(pname)

            # Use stmt.position to get the real source line
            ln = stmt.position.line if stmt.position else 1
            violations.append({
                "codeSmellType": "Reassigning Parameter",
                "filename":      filename,
                "filepath":      filepath,
                "startline":     ln,
                "endline":       ln,
                "code":          "RP",
                "category":      "Best Practices",
                "weight":        SMELL_CATEGORY_WEIGHTS.get("Reassigning Parameter", 2)
            })

            if reported == params:
                break

    return violations or None
