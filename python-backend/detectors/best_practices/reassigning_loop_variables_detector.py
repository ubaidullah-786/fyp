import javalang
from javalang.ast import walk_tree
from javalang.tree import (
    ForStatement,
    ForControl,
    EnhancedForControl,
    VariableDeclaration,
    MemberReference,
    Assignment
)
from ..thresholds import SMELL_CATEGORY_WEIGHTS

def get_variable_usages(node, var_names):
    usages = []
    for path, child in walk_tree(node):
        if isinstance(child, MemberReference) and child.member in var_names:
            usages.append((child, path))
    return usages

def is_write_usage(usage, path):
    parent = path[-1] if path else None
    # direct assignment to the variable?
    if isinstance(parent, Assignment) and parent.expressionl == usage:
        return True
    # ++/-- attached?
    if getattr(usage, 'prefix_operators', None):
        if any(op in ('++', '--') for op in usage.prefix_operators):
            return True
    if getattr(usage, 'postfix_operators', None):
        if any(op in ('++', '--') for op in usage.postfix_operators):
            return True
    return False

def detect_reassigning_loop_variables(node, source_lines, filepath, filename,
                                      foreach_reassign='deny',
                                      for_reassign='deny'):
    """
    Flags writes (++/--/assignment) to loop-control variables in both:
      - enhanced-for loops (EnhancedForControl)
      - traditional for loops (ForControl)
    """
    if not isinstance(node, ForStatement):
        return None

    violations = []
    ctrl = node.control
    loop_vars = set()

    # --- collect loop variable names ---
    if isinstance(ctrl, EnhancedForControl):
        # ctrl.var might be a VariableDeclaration or a simple parameter node
        var_node = ctrl.var
        if isinstance(var_node, VariableDeclaration):
            for d in var_node.declarators:
                loop_vars.add(d.name)
        else:
            # likely a FormalParameter-like node
            loop_vars.add(var_node.name)

        mode = foreach_reassign

    elif isinstance(ctrl, ForControl):
        # ctrl.init is a list of init elements (vars or exprs)
        if ctrl.init:
            for init_item in ctrl.init:
                if isinstance(init_item, VariableDeclaration):
                    for d in init_item.declarators:
                        loop_vars.add(d.name)
        mode = for_reassign

    else:
        return None  # not a for‐loop we care about

    # --- if the mode is "deny", find any writes ---
    if mode == 'deny' and loop_vars:
        for usage, path in get_variable_usages(node.body, loop_vars):
            if is_write_usage(usage, path):
                line = usage.position.line if usage.position else 1
                violations.append({
                    "codeSmellType": "Reassigning Loop Variable",
                    "filename": filename,
                    "filepath": filepath,
                    "startline": line,
                    "endline":   line,
                    "code":      "RLV",
                    "category":  "Best Practices",
                    "weight":    SMELL_CATEGORY_WEIGHTS.get("Reassigning Loop Variable", 2)
                })

    return violations or None 