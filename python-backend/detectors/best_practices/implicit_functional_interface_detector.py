import javalang
from javalang.tree import InterfaceDeclaration, MethodDeclaration, Annotation
from javalang.ast import walk_tree
from ..thresholds import SMELL_CATEGORY_WEIGHTS

def detect_implicit_functional_interface(node, source_lines, filepath, filename):
    if not isinstance(node, InterfaceDeclaration):
        return None

    # 1) Gather annotation names
    ann_names = {a.name for a in node.annotations}

    # 2) If annotated @FunctionalInterface → OK
    if 'FunctionalInterface' in ann_names:
        return None

    # 3) If suppressed explicitly → OK
    suppressions = set()
    for annot in node.annotations:
        if annot.name == 'SuppressWarnings' and annot.element is not None:
            for _, lit in walk_tree(annot.element):
                if isinstance(lit, javalang.tree.Literal):
                    suppressions.add(lit.value.strip('"').strip("'"))
    if 'PMD.ImplicitFunctionalInterface' in suppressions:
        return None

    # 4) If any default methods exist → OK
    for member in node.body:
        if isinstance(member, MethodDeclaration) and 'default' in getattr(member, 'modifiers', ()):
            return None

    # 5) Count abstract (non-static, non-private) methods
    abstract_count = 0
    for member in node.body:
        if isinstance(member, MethodDeclaration):
            mods = getattr(member, 'modifiers', set())
            if 'static' in mods or 'private' in mods:
                continue
            # At this point it's abstract (no default)
            abstract_count += 1
            if abstract_count > 1:
                break

    # 6) If exactly one abstract method → implicit functional
    if abstract_count == 1:
        ln = node.position.line if node.position else 1
        return [{
            "codeSmellType": "Implicit Functional Interface",
            "filename":      filename,
            "filepath":      filepath,
            "startline":     ln,
            "endline":       ln,
            "code":          "IFI",
            "category":      "Best Practices",
            "weight":        SMELL_CATEGORY_WEIGHTS.get("Implicit Functional Interface", 1)
        }]

    return None
