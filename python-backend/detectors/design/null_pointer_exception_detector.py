import javalang
from ..thresholds import SMELL_CATEGORY_WEIGHTS

def detect_null_pointer_exception(node, source_lines, filepath, filename):
    if isinstance(node, javalang.tree.ThrowStatement):
        expr = node.expression
        if isinstance(expr, javalang.tree.ClassCreator):
            if hasattr(expr, 'type') and hasattr(expr.type, 'name'):
                if expr.type.name == 'NullPointerException':
                    start_line = node.position.line if node.position else 1
                    return {
                        "codeSmellType": "Throwing NullPointerException",
                        "filename": filename,
                        "filepath": filepath,
                        "startline": start_line,
                        "endline": start_line,
                        "code": "NPD",
                        "category": "Design",
                        "weight": SMELL_CATEGORY_WEIGHTS.get("Throwing NullPointerException", 4)
                    }
    return None
