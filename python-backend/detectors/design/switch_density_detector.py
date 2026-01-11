import javalang
from ..thresholds import SWITCH_DENSITY_THRESHOLD, SMELL_CATEGORY_WEIGHTS

def detect_switch_density(node, source_lines, filepath, filename):
    if isinstance(node, javalang.tree.MethodDeclaration):
        for path, child in javalang.ast.walk_tree(node):
            if isinstance(child, javalang.tree.SwitchStatement):
                total_cases = 0
                for case_group in child.cases:
                    if case_group is not None and hasattr(case_group, 'case'):
                        # Count each case label separately
                        if case_group.case is None:
                            total_cases += 1  # 'default' case
                        elif isinstance(case_group.case, list):
                            total_cases += len(case_group.case)
                        else:
                            total_cases += 1  # Single case label

                if total_cases > SWITCH_DENSITY_THRESHOLD:
                    # ✅ Use the position of the switch statement
                    start_line = child.position.line if child.position else (node.position.line if node.position else 1)

                    brace_count = 0
                    end_line = start_line
                    for i, line in enumerate(source_lines[start_line - 1:], start=start_line):
                        brace_count += line.count('{') - line.count('}')
                        if brace_count == 0 and '}' in line:
                            end_line = i
                            break

                    return {
                        "codeSmellType": "High Switch Density",
                        "filename": filename,
                        "filepath": filepath,
                        "startline": start_line,
                        "endline": end_line,
                        "code": "SWD",
                        "category": "Design",
                        "weight": SMELL_CATEGORY_WEIGHTS.get("Switch Density", 3)
                    }
        return None
    return None
