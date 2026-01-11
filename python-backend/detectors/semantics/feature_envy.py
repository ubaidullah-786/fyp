"""
Feature Envy Detector

Detects Feature Envy code smell using a trained model.
Similar structure to complex_method.py
"""

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import os
from ..thresholds import SMELL_CATEGORY_WEIGHTS

# Get the directory of the current file
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))

# Load model from local directories
model_path = os.path.join(project_root, "feature-envy")
tokenizer_path = os.path.join(project_root, "feature-envy")

# Load tokenizer and model from local paths
tokenizer = AutoTokenizer.from_pretrained(tokenizer_path, local_files_only=True)
model = AutoModelForSequenceClassification.from_pretrained(model_path, local_files_only=True)

# Optimization: Set model to eval mode and use GPU if available
model.eval()
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)


def detect_feature_envy_batch(code_samples):
    """
    Detect Feature Envy for multiple code samples in a batch.
    
    Args:
        code_samples: List of preprocessed Java code samples
        
    Returns:
        List of booleans - True if Feature Envy detected for each sample
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


def detect_feature_envy(code_sample):
    """
    Detect if a code sample exhibits Feature Envy smell.
    
    Args:
        code_sample: Preprocessed Java code sample
        
    Returns:
        True if Feature Envy is detected (prediction == 1), False otherwise
    """
    results = detect_feature_envy_batch([code_sample])
    return results[0] if results else False


def detect_feature_envy_smell(node, source_lines, filepath, filename):
    """
    Detect Feature Envy smell in a Java method.
    
    Args:
        node: AST node (MethodDeclaration)
        source_lines: List of source code lines
        filepath: Full path to the file
        filename: Name of the file
        
    Returns:
        List of smell dicts if detected, empty list otherwise
    """
    import javalang.tree
    from .feature_envy_preprocessor import preprocess_java_file
    
    # Only process at CompilationUnit level to avoid duplicate processing
    if not isinstance(node, javalang.tree.CompilationUnit):
        return []
    
    results = []
    
    # Reconstruct content from source lines
    content = '\n'.join(source_lines)
    
    # Get preprocessed samples
    samples = preprocess_java_file(content, filepath, filename)
    
    if not samples:
        return []
    
    # Extract all code samples for batch processing
    code_samples = [sample['code_sample'] for sample in samples if sample.get('code_sample')]
    
    if not code_samples:
        return []
    
    # Batch inference - much faster than one-by-one
    predictions = detect_feature_envy_batch(code_samples)
    
    # Match predictions back to samples
    valid_samples = [s for s in samples if s.get('code_sample')]
    for sample, is_feature_envy in zip(valid_samples, predictions):
        if is_feature_envy:
            results.append({
                "codeSmellType": "Feature Envy",
                "filename": filename,
                "filepath": filepath,
                "startline": sample['start_line'],
                "endline": sample['end_line'],
                "code": "FE",
                "category": "Semantic Based",
                "weight": SMELL_CATEGORY_WEIGHTS.get("Feature Envy", 3)
            })
    
    return results