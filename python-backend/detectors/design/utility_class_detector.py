import javalang
from ..thresholds import SMELL_CATEGORY_WEIGHTS

def detect_utility_class(node, source_lines, filepath, filename):
    if isinstance(node, javalang.tree.ClassDeclaration):
        if node.modifiers and 'abstract' in node.modifiers:
            return None
        methods = node.methods
        if not methods:
            return None
        all_static = all('static' in method.modifiers for method in methods if isinstance(method, javalang.tree.MethodDeclaration))
        has_non_private_constructor = any(
            isinstance(decl, javalang.tree.ConstructorDeclaration) and 'private' not in decl.modifiers
            for decl in node.constructors
        )
        if all_static and (not node.constructors or has_non_private_constructor):
            start_line = node.position.line if node.position else 1
            brace_count = 0
            end_line = start_line
            for i, line in enumerate(source_lines[start_line-1:], start=start_line):
                brace_count += line.count('{') - line.count('}')
                if brace_count == 0 and '}' in line:
                    end_line = i
                    break
            return {
                "codeSmellType": "Utility Class",
                "filename": filename,
                "filepath": filepath,
                "startline": start_line,
                "endline": end_line,
                "code": "UTD",
                "category": "Design",
                "weight": SMELL_CATEGORY_WEIGHTS.get("Utility Class", 1)
            }
    return None