import javalang
from javalang.tree import (
    LocalVariableDeclaration,
    MemberReference,
    Assignment,
)
from javalang.ast import walk_tree
from ..thresholds import SMELL_CATEGORY_WEIGHTS

# Cache full ASTs per file to avoid reparsing
_ast_cache = {}
_IGNORED_PREFIXES = ("ignored", "unused")

def _is_read_usage(ref, path):
    parent = path[-1] if path else None
    return not (isinstance(parent, Assignment) and parent.expressionl is ref)

def detect_unused_local_variable(node, source_lines, filepath, filename):
    # Only handle local var declarations
    if not isinstance(node, LocalVariableDeclaration):
        return None

    # Build or fetch full AST for this file
    if filepath not in _ast_cache:
        code = "\n".join(source_lines)
        try:
            _ast_cache[filepath] = javalang.parse.parse(code)
        except javalang.parser.JavaSyntaxError:
            _ast_cache[filepath] = None
    tree = _ast_cache[filepath]
    if tree is None:
        return None

    # Gather all read‐uses for each name in the file
    reads = {}
    for path, child in walk_tree(tree):
        if isinstance(child, MemberReference):
            name = child.member
            if name not in reads:
                reads[name] = []
            if _is_read_usage(child, path):
                reads[name].append(child)

    violations = []
    for decl in node.declarators:
        name = decl.name
        # Skip ignored prefixes
        if any(name.startswith(p) for p in _IGNORED_PREFIXES):
            continue

        used = bool(reads.get(name))

        if not used:
            ln = decl.position.line if decl.position else node.position.line
            violations.append({
                "codeSmellType": "Unused Local Variable",
                "filename":      filename,
                "filepath":      filepath,
                "startline":     ln,
                "endline":       ln,
                "code":          "ULV",
                "category":      "Best Practices",
                "weight":        SMELL_CATEGORY_WEIGHTS.get("Unused Local Variable", 1)
            })

    return violations or None
