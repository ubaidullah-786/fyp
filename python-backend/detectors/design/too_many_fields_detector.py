import javalang
from ..thresholds import TOO_MANY_FIELDS_THRESHOLD, SMELL_CATEGORY_WEIGHTS

def detect_too_many_fields(node, source_lines, filepath, filename):
    if isinstance(node, javalang.tree.ClassDeclaration):
        # Filter: only non-static and non-final fields
        non_static_non_final_fields = [
            field for field in node.fields
            if 'static' not in field.modifiers and 'final' not in field.modifiers
        ]

        field_count = len(non_static_non_final_fields)
        # print(field_count)
        if field_count > TOO_MANY_FIELDS_THRESHOLD:
            start_line = node.position.line if node.position else 1
            brace_count = 0
            end_line = start_line

            # Bracket matching to find class end
            for i, line in enumerate(source_lines[start_line - 1:], start=start_line):
                brace_count += line.count('{') - line.count('}')
                if brace_count == 0 and '}' in line:
                    end_line = i
                    break

            return {
                "codeSmellType": "Too Many Fields",
                "filename": filename,
                "filepath": filepath,
                "startline": start_line,
                "endline": end_line,
                "code": "TMF",
                "category": "Design",
                "weight": SMELL_CATEGORY_WEIGHTS.get("Too Many Fields", 3)
            }

    return None
