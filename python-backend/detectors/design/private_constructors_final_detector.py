import javalang
from ..thresholds import SMELL_CATEGORY_WEIGHTS

def detect_private_constructors_final(node, source_lines, filepath, filename):
    if isinstance(node, javalang.tree.ClassDeclaration):
        if 'final' in node.modifiers:
            return None
        constructors = node.constructors
        if not constructors:  # No constructors, implicit public constructor
            return None
        all_private = all('private' in c.modifiers for c in constructors)
        if all_private:
            start_line = node.position.line if node.position else 1
            brace_count = 0
            end_line = start_line
            for i, line in enumerate(source_lines[start_line-1:], start=start_line):
                brace_count += line.count('{') - line.count('}')
                if brace_count == 0 and '}' in line:
                    end_line = i
                    break
            return {
                "codeSmellType": "Class With Only Private Constructors Should Be Final",
                "filename": filename,
                "filepath": filepath,
                "startline": start_line,
                "endline": end_line,
                "code": "PRV",
                "category": "Design",
                "weight": SMELL_CATEGORY_WEIGHTS.get("Private Constructor Check", 1)
            }
    return None