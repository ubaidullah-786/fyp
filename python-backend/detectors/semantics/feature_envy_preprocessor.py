"""
Feature Envy Preprocessor

Preprocesses Java code to create minimal code samples for Feature Envy detection.
Creates samples with: method_name, start_line, end_line, code_sample
"""

import re
import javalang
from collections import defaultdict
from typing import Dict, List, Set, Optional


class ClassData:
    def __init__(self, name, fqn):
        self.name = name
        self.fqn = fqn
        self.methods = {}
        self.parent_class = None


class MethodData:
    def __init__(self, name, source, start_line, end_line):
        self.name = name
        self.source = source
        self.start_line = start_line
        self.end_line = end_line
        self.external_calls = defaultdict(set)


class FeatureEnvyPreprocessor:
    """Preprocesses Java code for Feature Envy detection"""
    
    def __init__(self):
        self.classes = {}  # fqn -> ClassData
    
    def preprocess_file(self, content: str, filepath: str, filename: str) -> List[Dict]:
        """
        Preprocess a Java file and extract samples for Feature Envy detection.
        
        Returns:
            List of dicts with: method_name, start_line, end_line, code_sample
        """
        samples = []
        self.classes = {}
        
        try:
            processed_content = self._preprocess_content(content)
            tree = javalang.parse.parse(processed_content)
            package = tree.package.name if tree.package else ""
            
            # Extract all classes
            for type_decl in tree.types:
                if not hasattr(type_decl, 'name') or not hasattr(type_decl, 'body'):
                    continue
                
                class_name = self._get_name(type_decl.name)
                if not class_name or class_name == "Main":
                    continue
                
                fqn = f"{package}.{class_name}" if package else class_name
                class_data = ClassData(class_name, fqn)
                
                # Extract parent class
                if hasattr(type_decl, 'extends') and type_decl.extends:
                    parent_class = self._get_name(type_decl.extends.name)
                    class_data.parent_class = parent_class
                
                # Extract methods
                if hasattr(type_decl, 'body') and type_decl.body:
                    for member in type_decl.body:
                        if isinstance(member, javalang.tree.MethodDeclaration):
                            method = self._extract_method(member, processed_content, fqn)
                            if method:
                                class_data.methods[method.name] = method
                
                if class_data.methods:
                    self.classes[fqn] = class_data
            
            # Generate samples
            samples = self._generate_samples()
            
        except (javalang.parser.JavaSyntaxError, javalang.tokenizer.LexerError):
            pass
        except Exception:
            pass
        
        return samples
    
    def _get_name(self, name):
        """Extract string name from various types"""
        if isinstance(name, list):
            return str(name[0]) if name else None
        elif isinstance(name, str):
            return name
        else:
            return str(name) if name else None
    
    def _preprocess_content(self, content):
        """Pre-process Java content to handle common parsing issues"""
        content = re.sub(r'@SuppressWarnings\([^)]*\)', '@SuppressWarnings("all")', content)
        content = re.sub(r'->\s*\{[^}]*\}', '-> {}', content)
        content = re.sub(r'\s*->\s*[^;,}\n]+', ' -> null', content)
        content = re.sub(r'::[a-zA-Z_][a-zA-Z0-9_]*', '::method', content)
        content = re.sub(r'@Override\s*', '', content)
        content = re.sub(r'@Deprecated\s*', '', content)
        return content
    
    def _extract_method(self, method_decl, content, class_fqn):
        """Extract method with its source code and line numbers"""
        try:
            method_name = self._get_name(method_decl.name)
            if not method_name:
                return None
            
            lines = content.splitlines()
            start_line = method_decl.position.line if method_decl.position else 1
            
            # Get method source and end line
            method_source, end_line = self._get_method_source(lines, start_line - 1, method_name)
            
            if not method_source:
                return None
            
            method = MethodData(method_name, method_source, start_line, end_line)
            
            # Find external method calls
            if hasattr(method_decl, 'filter'):
                for _, node in method_decl.filter(javalang.tree.MethodInvocation):
                    if hasattr(node, 'qualifier') and node.qualifier:
                        qualifier_str = str(node.qualifier)
                        member = str(node.member) if node.member else "unknown"
                        
                        # Skip system calls and built-in Java classes
                        skip_prefixes = ['this', 'super', 'System', 'String', 
                                        'Integer', 'Collections', 'Arrays', 'Math']
                        if not any(qualifier_str.startswith(p) for p in skip_prefixes):
                            base_qualifier = qualifier_str.split('.')[0]
                            if base_qualifier:
                                method.external_calls[base_qualifier].add(member)
            
            return method
            
        except Exception:
            return None
    
    def _get_method_source(self, lines, start_idx, method_name):
        """Get method source code and calculate end line"""
        try:
            # Find method start
            method_start = start_idx
            for i in range(max(0, start_idx - 2), min(start_idx + 5, len(lines))):
                if i < len(lines) and method_name in lines[i] and '(' in lines[i]:
                    method_start = i
                    break
            
            # Find method end by counting braces
            brace_count = 0
            end_line = method_start + 1
            found_opening_brace = False
            
            for i in range(method_start, min(method_start + 100, len(lines))):
                if i >= len(lines):
                    break
                
                line = lines[i]
                for char in line:
                    if char == '{':
                        brace_count += 1
                        found_opening_brace = True
                    elif char == '}':
                        brace_count -= 1
                        if found_opening_brace and brace_count == 0:
                            end_line = i + 1  # 1-based
                            return '\n'.join(lines[method_start:i + 1]), end_line
                
                # Abstract method
                if not found_opening_brace and ';' in line:
                    return '\n'.join(lines[method_start:i + 1]), i + 1
            
            # Fallback
            end_line = min(method_start + 20, len(lines))
            return '\n'.join(lines[method_start:end_line]), end_line
            
        except Exception:
            return "", start_idx + 1
    
    def _is_getter_setter(self, method):
        """Check if method is a simple getter or setter"""
        source = method.source.lower()
        lines = [l.strip() for l in method.source.splitlines() if l.strip()]
        
        if method.name.startswith(('get', 'is')) and len(lines) <= 5:
            if 'return' in source and source.count('return') == 1:
                return True
        
        if method.name.startswith('set') and len(lines) <= 5:
            if ('=' in source or 'this.' in source) and 'return' not in source:
                return True
        
        return False
    
    def _generate_samples(self) -> List[Dict]:
        """Generate model-ready samples from extracted classes"""
        samples = []
        
        for class_fqn, class_data in self.classes.items():
            for method_name, method in class_data.methods.items():
                # Skip getter/setter methods
                if self._is_getter_setter(method):
                    continue
                
                # Only process methods with external calls
                if not method.external_calls:
                    continue
                
                code_sample = self._create_minimal_sample(class_data, method)
                
                if code_sample:
                    samples.append({
                        'method_name': method_name,
                        'class_name': class_data.name,
                        'start_line': method.start_line,
                        'end_line': method.end_line,
                        'code_sample': code_sample,
                        'external_calls': dict(method.external_calls)
                    })
        
        return samples
    
    def _create_minimal_sample(self, class_data, method):
        """Create minimal code sample for model inference"""
        lines = []
        
        # Main class header
        lines.append(f"class {class_data.name} {{")
        
        # Add the method (indented)
        method_lines = self._remove_comments(method.source).splitlines()
        for line in method_lines:
            if line.strip():
                lines.append(f"    {line}")
        
        lines.append("}")
        
        # Add referenced classes with only called methods
        for qualifier, called_methods in method.external_calls.items():
            ref_class = self._find_class_by_name(qualifier)
            if ref_class:
                lines.append("")
                lines.append(f"class {ref_class.name} {{")
                
                for called_method in list(called_methods):
                    if called_method in ref_class.methods:
                        ref_method_source = self._remove_comments(ref_class.methods[called_method].source)
                        for line in ref_method_source.splitlines():
                            if line.strip():
                                lines.append(f"    {line}")
                    else:
                        # Create stub method if not found
                        lines.append(f"    public void {called_method}() {{}}")
                
                lines.append("}")
            else:
                # Create stub class for external classes not found in the file
                lines.append("")
                lines.append(f"class {qualifier} {{")
                for called_method in list(called_methods):
                    lines.append(f"    public void {called_method}() {{}}")
                lines.append("}")
        
        return '\n'.join(lines)
    
    def _find_class_by_name(self, name):
        """Find class by simple name"""
        for class_data in self.classes.values():
            if class_data.name == name or class_data.name.lower() == name.lower():
                return class_data
        return None
    
    def _remove_comments(self, source_code):
        """Remove comments from Java source code"""
        lines = source_code.splitlines()
        cleaned_lines = []
        in_block_comment = False
        
        for line in lines:
            cleaned_line = ""
            i = 0
            
            while i < len(line):
                if i < len(line) - 1 and line[i:i+2] == "/*":
                    in_block_comment = True
                    i += 2
                    continue
                
                if in_block_comment and i < len(line) - 1 and line[i:i+2] == "*/":
                    in_block_comment = False
                    i += 2
                    continue
                
                if not in_block_comment and i < len(line) - 1 and line[i:i+2] == "//":
                    break
                
                if not in_block_comment:
                    cleaned_line += line[i]
                
                i += 1
            
            if cleaned_line.strip():
                cleaned_lines.append(cleaned_line.rstrip())
        
        return '\n'.join(cleaned_lines)


def preprocess_java_file(content: str, filepath: str, filename: str) -> List[Dict]:
    """
    Convenience function to preprocess a Java file.
    
    Returns:
        List of samples with: method_name, class_name, start_line, end_line, code_sample
    """
    preprocessor = FeatureEnvyPreprocessor()
    return preprocessor.preprocess_file(content, filepath, filename)
