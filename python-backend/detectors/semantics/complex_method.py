
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import os
from ..thresholds import SMELL_CATEGORY_WEIGHTS

# Get the directory of the current file
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))

# Load model from local directory
model_path = os.path.join(project_root, "complex-method")
# Use feature-envy tokenizer since complex-method doesn't have tokenizer files
tokenizer_path = os.path.join(project_root, "feature-envy")

try:
    # Load tokenizer and model from local paths
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_path, local_files_only=True)
    model = AutoModelForSequenceClassification.from_pretrained(model_path, local_files_only=True)
except Exception as e:
    print(f"Error loading models: {e}")
    raise

# Optimization: Set model to eval mode and use GPU if available
model.eval()
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)


def detect_complex_method_batch(code_samples):
    """
    Detect Complex Method for multiple code samples in a batch.
    
    Args:
        code_samples: List of code snippets
        
    Returns:
        List of booleans - True if Complex Method detected for each sample
    """
    if not code_samples:
        return []
    
    # Batch tokenization
    inputs = tokenizer(
        code_samples, 
        truncation=True, 
        max_length=512, 
        padding=True, 
        return_tensors="pt"
    )
    
    # Move inputs to device
    inputs = {k: v.to(device) for k, v in inputs.items()}
    
    with torch.no_grad():
        outputs = model(**inputs)
    
    predictions = torch.argmax(outputs.logits, dim=1).tolist()
    return [pred == 1 for pred in predictions]


def detect_complex_method(code):
    results = detect_complex_method_batch([code])
    return results[0] if results else False

def extract_method_code(source_lines, start_line):
    code = []
    brace_count = 0
    started = False

    for line in source_lines[start_line - 1:]:
        stripped = line.strip()
        if "{" in stripped:
            brace_count += stripped.count("{")
            started = True
        if "}" in stripped:
            brace_count -= stripped.count("}")
        code.append(line)
        if started and brace_count == 0:
            break

    return "\n".join(code)


def detect_complex_method_smell(node, source_lines, filepath, filename):
    """Process individual method nodes (backwards compatible)"""
    import javalang.tree

    if isinstance(node, javalang.tree.MethodDeclaration) and node.position:
        # Skip main method
        if node.name == "main":
            return None

        start_line = node.position.line
        code_snippet = extract_method_code(source_lines, start_line)

        if detect_complex_method(code_snippet):
            return {
                "codeSmellType": "Complex Method",
                "filename": filename,
                "filepath": filepath,
                "startline": start_line,
                "endline": start_line + code_snippet.count('\n'),
                "code": "CM",
                "category": "Sematic Based",
                "weight": SMELL_CATEGORY_WEIGHTS.get("Complex Method", 3)
            }

    return None


def detect_complex_method_smell_batch(node, source_lines, filepath, filename):
    """
    Batch process all methods in a CompilationUnit for Complex Method smell.
    Call this at CompilationUnit level for better performance.
    """
    import javalang.tree

    # Only process at CompilationUnit level
    if not isinstance(node, javalang.tree.CompilationUnit):
        return []
    
    # Collect all methods
    methods_data = []
    for path, method_node in node.filter(javalang.tree.MethodDeclaration):
        if method_node.position and method_node.name != "main":
            start_line = method_node.position.line
            code_snippet = extract_method_code(source_lines, start_line)
            methods_data.append({
                'start_line': start_line,
                'code_snippet': code_snippet,
                'end_line': start_line + code_snippet.count('\n')
            })
    
    if not methods_data:
        return []
    
    # Batch inference
    code_samples = [m['code_snippet'] for m in methods_data]
    predictions = detect_complex_method_batch(code_samples)
    
    # Build results
    results = []
    for method_info, is_complex in zip(methods_data, predictions):
        if is_complex:
            results.append({
                "codeSmellType": "Complex Method",
                "filename": filename,
                "filepath": filepath,
                "startline": method_info['start_line'],
                "endline": method_info['end_line'],
                "code": "CM",
                "category": "Sematic Based",
                "weight": SMELL_CATEGORY_WEIGHTS.get("Complex Method", 3)
            })
    
    return results
