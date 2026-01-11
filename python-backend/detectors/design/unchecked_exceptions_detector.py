import javalang
from ..thresholds import SMELL_CATEGORY_WEIGHTS

def detect_unchecked_exceptions(node, source_lines, filepath, filename):
    if isinstance(node, (javalang.tree.MethodDeclaration, javalang.tree.ConstructorDeclaration)):
        if node.throws:
            unchecked_exceptions = {'RuntimeException', 'Error'}
            for exception in node.throws:
                exception_name = exception.name if isinstance(exception, javalang.tree.ReferenceType) else exception
                if exception_name in unchecked_exceptions:
                    start_line = node.position.line if node.position else 1
                    brace_count = 0
                    end_line = start_line
                    for i, line in enumerate(source_lines[start_line-1:], start=start_line):
                        brace_count += line.count('{') - line.count('}')
                        if brace_count == 0 and '}' in line:
                            end_line = i
                            break
                    return {
                        "codeSmellType": "Unchecked Exceptions In Signatures",
                        "filename": filename,
                        "filepath": filepath,
                        "startline": start_line,
                        "endline": end_line,
                        "code": "UCD",
                        "category": "Design",
                        "weight": SMELL_CATEGORY_WEIGHTS.get("Unchecked Exceptions", 3)
                    }
    return None