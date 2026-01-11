"""
Code Smell Detection Thresholds Configuration

This centralized configuration file contains all thresholds used by various 
code smell detectors. Modify these values to adjust detection sensitivity.

All values are integers representing count-based or complexity-based metrics.
"""

# =============================================================================
# DESIGN PATTERN THRESHOLDS
# =============================================================================

# Too Many Methods Detector
# Threshold: Number of non-getter/setter methods in a class before triggering smell
TOO_MANY_METHODS_THRESHOLD = 10

# Too Many Fields Detector
# Threshold: Number of non-static, non-final fields in a class before triggering smell
TOO_MANY_FIELDS_THRESHOLD = 15

# Cyclomatic Complexity Detector
# Threshold: McCabe complexity score for methods
# Complexity increases with: if, for, while, do, switch, ternary, &&, || operators
CYCLOMATIC_COMPLEXITY_THRESHOLD = 10

# Excessive Parameter List Detector
# Threshold: Number of parameters in method/constructor declarations
EXCESSIVE_PARAMETER_LIST_THRESHOLD = 10

# Excessive Imports Detector
# Threshold: Total number of import statements in a file
EXCESSIVE_IMPORTS_THRESHOLD = 30

# Nested If Detector
# Threshold: Maximum allowed nesting depth for if statements
NESTED_IF_THRESHOLD = 3

# Switch Density Detector
# Threshold: Number of case statements in a switch before triggering smell
SWITCH_DENSITY_THRESHOLD = 10

# Utility Class Detector
# Threshold: Percentage of static methods required to classify as Utility Class
UTILITY_CLASS_STATIC_METHOD_THRESHOLD = 0.8  # 80% of methods must be static

# Private Constructors Final Detector
# Thresholds for detecting classes that should have private constructors
PRIVATE_CONSTRUCTORS_MAX_STATIC_METHODS = 5  # Class with mostly static members

# =============================================================================
# EXCEPTION HANDLING THRESHOLDS
# =============================================================================

# Unchecked Exceptions Detector
# Detects when code throws unchecked runtime exceptions
# No threshold - detects any occurrence of RuntimeException, etc.

# Raw Exception Types Detector
# Detects catch blocks using generic Exception class
# No threshold - detects any occurrence of catch(Exception e)

# Null Pointer Exception Detector
# Detects explicit throws of NullPointerException
# No threshold - detects any explicit throw

# =============================================================================
# BEST PRACTICES THRESHOLDS
# =============================================================================

# Reassigning Catch Variables Detector
# Detects modification of exception variable in catch block
# No threshold - detects any reassignment

# Reassigning Loop Variables Detector
# Detects modification of loop control variables inside loop body
# No threshold - detects any reassignment

# Reassigning Parameters Detector
# Detects modification of method parameters inside method body
# No threshold - detects any reassignment

# Result Set Check Detector
# Detects unchecked ResultSet operations (database operations)
# No threshold - detects patterns of unsafe database access

# Expensive Log Statement Detector
# Detects object creation or method calls inside log statements
# No threshold - detects any expensive operation in logging

# Literals First in Comparison Detector
# Detects comparisons where variable is on left side of literal
# Recommends: literal.equals(variable) instead of variable.equals(literal)
# No threshold - detects pattern-based occurrences

# Implicit Functional Interface Detector
# Detects single-method interfaces that should be functional interfaces
# No threshold - detects by interface structure

# Unused Local Variable Detector
# Detects local variables that are declared but never used
# No threshold - detects by usage analysis

# =============================================================================
# ML-BASED DETECTORS (No explicit thresholds - uses trained models)
# =============================================================================

# Complex Method Detector
# Uses transformer-based ML model to detect methods that are too complex
# Model outputs: 0 (simple) or 1 (complex)
# No configurable threshold

# Feature Envy Detector
# Uses transformer-based ML model to detect methods that use other classes excessively
# Model outputs: 0 (normal) or 1 (feature envy)
# No configurable threshold

# =============================================================================
# SEVERITY/WEIGHT MAPPING
# =============================================================================

# Code smell weights/severity levels
SEVERITY_WEIGHTS = {
    "HIGH": 4,      # Critical issues that must be fixed
    "MEDIUM": 3,    # Important issues that should be fixed
    "LOW": 2,       # Minor issues that could be improved
    "INFO": 1,      # Informational, lowest priority
}

# Default weights for each smell category
SMELL_CATEGORY_WEIGHTS = {
    # Design Patterns
    "High Cyclomatic Complexity (Method)": 3,
    "Too Many Methods": 3,
    "Too Many Fields": 3,
    "Utility Class": 1,
    "Switch Density": 3,
    "Excessive Parameter List": 2,
    "Excessive Imports": 2,
    "Nested If": 2,
    "Private Constructor Check": 1,
    
    # Exception Handling
    "Unchecked Exceptions": 3,
    "Raw Exception Types": 2,
    "Throwing NullPointerException": 4,
    
    # Best Practices
    "Reassigning Parameter": 2,
    "Reassigning Loop Variable": 2,
    "Reassigning Catch Variable": 2,
    "Result Set Check": 2,
    "Expensive Log Statement": 1,
    "Literals First in Comparison": 1,
    
    # Semantic-Based (ML)
    "Complex Method": 3,
    "Feature Envy": 3,
}

# =============================================================================
# DETECTOR CONFIGURATION
# =============================================================================

# Configuration dictionary for easy access
DETECTOR_CONFIG = {
    # Design Pattern Detectors
    "too_many_methods": {
        "threshold": TOO_MANY_METHODS_THRESHOLD,
        "description": "Class with too many methods",
        "weight": 3,
    },
    "too_many_fields": {
        "threshold": TOO_MANY_FIELDS_THRESHOLD,
        "description": "Class with too many fields",
        "weight": 3,
    },
    "cyclomatic_complexity": {
        "threshold": CYCLOMATIC_COMPLEXITY_THRESHOLD,
        "description": "Method with high cyclomatic complexity",
        "weight": 3,
    },
    "excessive_parameter_list": {
        "threshold": EXCESSIVE_PARAMETER_LIST_THRESHOLD,
        "description": "Method with excessive parameters",
        "weight": 2,
    },
    "excessive_imports": {
        "threshold": EXCESSIVE_IMPORTS_THRESHOLD,
        "description": "File with excessive imports",
        "weight": 2,
    },
    "nested_if": {
        "threshold": NESTED_IF_THRESHOLD,
        "description": "Deeply nested if statements",
        "weight": 2,
    },
    "switch_density": {
        "threshold": SWITCH_DENSITY_THRESHOLD,
        "description": "Switch statement with many cases",
        "weight": 3,
    },
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_threshold(detector_name: str) -> int:
    """
    Get the threshold value for a specific detector.
    
    Args:
        detector_name: Name of the detector (e.g., 'too_many_methods')
    
    Returns:
        Threshold value as integer
    """
    if detector_name in DETECTOR_CONFIG:
        return DETECTOR_CONFIG[detector_name]["threshold"]
    raise ValueError(f"Unknown detector: {detector_name}")


def get_weight(detector_name: str) -> int:
    """
    Get the severity weight for a specific detector.
    
    Args:
        detector_name: Name of the detector
    
    Returns:
        Weight value as integer
    """
    if detector_name in DETECTOR_CONFIG:
        return DETECTOR_CONFIG[detector_name]["weight"]
    raise ValueError(f"Unknown detector: {detector_name}")


def get_detector_description(detector_name: str) -> str:
    """
    Get the description for a specific detector.
    
    Args:
        detector_name: Name of the detector
    
    Returns:
        Description string
    """
    if detector_name in DETECTOR_CONFIG:
        return DETECTOR_CONFIG[detector_name]["description"]
    raise ValueError(f"Unknown detector: {detector_name}")


# =============================================================================
# USAGE EXAMPLES
# =============================================================================

"""
Example usage in detector files:

from thresholds import (
    TOO_MANY_METHODS_THRESHOLD,
    get_threshold,
    SMELL_CATEGORY_WEIGHTS
)

# Direct import
if method_count > TOO_MANY_METHODS_THRESHOLD:
    # Detect smell
    pass

# Using helper function
threshold = get_threshold('too_many_methods')
if method_count > threshold:
    # Detect smell
    pass

# Using weight mapping
weight = SMELL_CATEGORY_WEIGHTS.get("Too Many Methods", 3)
"""
