import javalang
from javalang.ast import walk_tree
from javalang.tree import (
    StatementExpression,
    MethodInvocation,
    IfStatement,
    Literal,
    MemberReference,
    BinaryOperation,
)
from ..thresholds import SMELL_CATEGORY_WEIGHTS

# Which logging calls we care about
LOG_LEVELS = {
    "trace", "debug", "info", "warn", "error",
    "log", "finest", "finer", "fine", "warning", "severe"
}

# What guard methods correspond
GUARD_METHODS = {
    "trace": {"isTraceEnabled"},
    "debug": {"isDebugEnabled"},
    "info":  {"isInfoEnabled"},
    "warn":  {"isWarnEnabled"},
    "error": {"isErrorEnabled"},
    # java.util.logging
    "log": {"isLoggable"},
    "finest": {"isLoggable"},
    "finer":  {"isLoggable"},
    "fine":   {"isLoggable"},
    "warning":{"isLoggable"},
    "severe": {"isLoggable"},
}

def detect_expensive_log_statement(node, source_lines, filepath, filename, **kwargs):
    if not isinstance(node, StatementExpression):
        return None

    mi = node.expression
    if not isinstance(mi, MethodInvocation):
        return None

    level = mi.member
    if level not in LOG_LEVELS:
        return None

    # 2) Check for a surrounding if‐guard
    guarded = False
    parent = getattr(node, 'parent', None)
    while parent:
        if isinstance(parent, IfStatement):
            # inspect its condition subtree for a guard call
            for _, cond_node in walk_tree(parent.condition):
                if (isinstance(cond_node, MethodInvocation)
                    and cond_node.member in GUARD_METHODS.get(level, ())
                    # java.util.logging: must also match Level argument,
                    # but we'll skip that extra check here for brevity
                   ):
                    guarded = True
                    break
            if guarded:
                return None

        parent = getattr(parent, 'parent', None)

    args = mi.arguments or []
    is_expensive = False

    # check for concatenation
    for arg in args:
        if isinstance(arg, BinaryOperation) and arg.operator == '+':
            is_expensive = True
            break

    # if no concat, check single-arg MethodInvocation
    if not is_expensive and len(args) == 1 and isinstance(args[0], MethodInvocation):
        is_expensive = True

    # simple literals or multi-arg substitution are fine
    if not is_expensive:
        return None

    ln = node.position.line if node.position else 1
    return [{
        "codeSmellType": "Expensive Log Statement",
        "filename":      filename,
        "filepath":      filepath,
        "startline":     ln,
        "endline":       ln,
        "code":          "ELS",
        "category":      "Best Practices",
        "weight":        SMELL_CATEGORY_WEIGHTS.get("Expensive Log Statement", 1)
    }]
