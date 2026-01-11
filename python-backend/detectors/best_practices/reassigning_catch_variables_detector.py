import javalang
from javalang.ast import walk_tree
from ..thresholds import SMELL_CATEGORY_WEIGHTS

def detect_reassigning_catch_variables(node, source_lines, filepath, filename, allow_private=True):
    # Ensure the node is a CatchClause
    if not isinstance(node, javalang.tree.CatchClause):
        return None

    # Get the catch parameter name
    param = node.parameter
    var_name = param.name
    violations = []

    # Traverse the catch block to find assignments
    for path, child in walk_tree(node.block):
        if isinstance(child, javalang.tree.StatementExpression):
            expr = child.expression
            if isinstance(expr, javalang.tree.Assignment):
                left = expr.expressionl
                # Check if the left-hand side is the catch variable
                if (isinstance(left, javalang.tree.MemberReference) and 
                    left.member == var_name):
                    # Get the line number from the ExpressionStatement's position
                    start_line = child.position.line if child.position else 1
                    violations.append({
                        "codeSmellType": "Reassigning Catch Variable",
                        "filename": filename,
                        "filepath": filepath,
                        "startline": start_line,
                        "endline": start_line,
                        "code": "RCV",
                        "category": "Best Practices",
                        "weight": SMELL_CATEGORY_WEIGHTS.get("Reassigning Catch Variable", 2)
                    })

    return violations if violations else None