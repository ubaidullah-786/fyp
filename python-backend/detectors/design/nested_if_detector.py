import javalang
import logging
from ..thresholds import NESTED_IF_THRESHOLD, SMELL_CATEGORY_WEIGHTS

# Configure logging

def get_max_if_depth(statement, current_depth=0):
    if isinstance(statement, javalang.tree.IfStatement):
        # Only count depth through then_statement, ignore else_statement for depth
        then_depth = get_max_if_depth(statement.then_statement, current_depth + 1) if statement.then_statement else current_depth + 1
        # Do not count else branch in depth
        return then_depth
    elif hasattr(statement, 'statements') and isinstance(statement.statements, list):
        return max([get_max_if_depth(s, current_depth) for s in statement.statements] or [current_depth])
    elif isinstance(statement, list):
        return max([get_max_if_depth(s, current_depth) for s in statement] or [current_depth])
    return current_depth


def get_first_if_line_of_nested_chain(statement, target_depth=3, current_depth=0, first_if_line=None):
    """
    Recursively find the first if statement line number of the nested if chain
    with depth >= target_depth, counting depth only through then_statement branches.
    """
    if isinstance(statement, javalang.tree.IfStatement):
        # If this is the first if in the chain, record its line number
        if first_if_line is None and statement.position:
            first_if_line = statement.position.line

        if current_depth + 1 >= target_depth:
            return first_if_line
        
        # Only recurse into then_statement for depth counting
        if statement.then_statement:
            return get_first_if_line_of_nested_chain(statement.then_statement, target_depth, current_depth + 1, first_if_line)
    
    elif hasattr(statement, 'statements') and isinstance(statement.statements, list):
        for s in statement.statements:
            line = get_first_if_line_of_nested_chain(s, target_depth, current_depth, first_if_line)
            if line is not None:
                return line
    elif isinstance(statement, list):
        for s in statement:
            line = get_first_if_line_of_nested_chain(s, target_depth, current_depth, first_if_line)
            if line is not None:
                return line

    return None


def detect_nested_if(node, source_lines, filepath, filename):
    if isinstance(node, javalang.tree.MethodDeclaration):
        max_depth = get_max_if_depth(node.body)
        if max_depth >= NESTED_IF_THRESHOLD:
            # Find the first if statement line in the nested if chain
            start_line = get_first_if_line_of_nested_chain(node.body, target_depth=NESTED_IF_THRESHOLD)
            if start_line is None:
                start_line = node.position.line if node.position else 1

            brace_count = 0
            end_line = start_line
            for i, line in enumerate(source_lines[start_line-1:], start=start_line):
                brace_count += line.count('{') - line.count('}')
                if brace_count <= 0 and '}' in line:
                    end_line = i
                    break

            return {
                "codeSmellType": "Nested If Statements",
                "filename": filename,
                "filepath": filepath,
                "startline": start_line,
                "endline": end_line,
                "code": "NED",
                "category": "Design",
                "weight": SMELL_CATEGORY_WEIGHTS.get("Nested If", 2)
            }
    return None
