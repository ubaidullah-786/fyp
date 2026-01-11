import javalang
from ..thresholds import TOO_MANY_METHODS_THRESHOLD, SMELL_CATEGORY_WEIGHTS

def is_getter(method):
    return (
        (method.name.startswith('get') or method.name.startswith('is'))
        and len(method.parameters) == 0
        and method.return_type
        and method.return_type.name != 'void'
    )

def is_setter(method):
    return (
        method.name.startswith('set')
        and len(method.parameters) == 1
        and method.return_type
        and method.return_type.name == 'void'
    )

def detect_too_many_methods(node, source_lines, filepath, filename):
    if isinstance(node, javalang.tree.ClassDeclaration):
        non_getter_setter_methods = [
            method for method in node.methods
            if not (is_getter(method) or is_setter(method))
        ]

        method_count = len(non_getter_setter_methods)
      

        if method_count > TOO_MANY_METHODS_THRESHOLD:
            start_line = node.position.line if node.position else 1

            # Find the actual starting line of the class body (where the first '{' is)
            body_start_line = -1
            for i in range(start_line - 1, len(source_lines)):
                if '{' in source_lines[i]:
                    body_start_line = i + 1  # Convert index to line number
                    break

            if body_start_line == -1:
                body_start_line = start_line  # fallback

            # Begin brace counting from the body start
            brace_count = 0
            end_line = body_start_line

            for i in range(body_start_line - 1, len(source_lines)):
                line = source_lines[i]
                brace_count += line.count('{') - line.count('}')
                if brace_count == 0:
                    end_line = i + 1  # Convert index to line number
                    break

            return {
                "codeSmellType": "Too Many Methods",
                "filename": filename,
                "filepath": filepath,
                "startline": start_line,
                "endline": end_line,
                "code": "TMM",
                "category": "Design",
                "weight": SMELL_CATEGORY_WEIGHTS.get("Too Many Methods", 3)
            }

    return None
