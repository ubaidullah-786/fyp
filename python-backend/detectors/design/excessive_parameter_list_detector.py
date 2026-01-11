import javalang
from ..thresholds import EXCESSIVE_PARAMETER_LIST_THRESHOLD, SMELL_CATEGORY_WEIGHTS

def detect_excessive_parameter_list(node, source_lines, filepath, filename):
    # Check if the node is a method or constructor declaration
    if isinstance(node, (javalang.tree.MethodDeclaration, javalang.tree.ConstructorDeclaration)):
        # Count the parameters
        param_count = len(node.parameters)
        
        # Debug print to verify parameter count
        # print(f"Detected method/constructor '{node.name}' with {param_count} parameters")
        
        # Threshold check
        if param_count > EXCESSIVE_PARAMETER_LIST_THRESHOLD:
            # Determine start line
            if node.position and node.position.line:
                start_line = node.position.line
            else:
                # print(f"Warning: {node.name} has no position info")
                return None  # Skip if position is unknown
            
            # Initialize end_line and attempt to find the closing brace
            end_line = start_line
            brace_count = 0
            
            # Check if the method has a block (body)
            if hasattr(node, 'block') and node.block:
                # Use the block's position to get the end line directly
                end_line = node.block.position.line if node.block.position else start_line
            else:
                # Fallback: manually track braces (may not be reliable with nested blocks)
                try:
                    brace_count = 0
                    for i in range(start_line - 1, len(source_lines)):
                        line = source_lines[i]
                        brace_count += line.count('{') - line.count('}')
                        if brace_count <= 0:
                            end_line = i + 1  # Lines are 1-based
                            break
                except Exception as e:
                    # print(f"Error determining end line: {e}")
                    end_line = start_line  # Fallback to start line
            
            # Return the detected smell
            return {
                "codeSmellType": "Excessive Parameter List",
                "filename": filename,
                "filepath": filepath,
                "startline": start_line,
                "endline": end_line,
                "code": "EXP",
                "category": "Design",
                "weight": SMELL_CATEGORY_WEIGHTS.get("Excessive Parameter List", 2)
            }
    
    return None
