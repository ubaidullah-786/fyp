import zipfile
import javalang
from detectors.design import (
    utility_class_detector,
    too_many_methods_detector,
    too_many_fields_detector,
    switch_density_detector,
    excessive_parameter_list_detector,
    excessive_imports_detector,
    cyclomatic_complexity_detector,
    private_constructors_final_detector,
    unchecked_exceptions_detector,
    raw_exception_types_detector,
    null_pointer_exception_detector,
    nested_if_detector,
)
from detectors.semantics import complex_method
from detectors.semantics import feature_envy

from detectors.best_practices import (
    reassigning_catch_variables_detector,
    reassigning_loop_variables_detector,
    reassigning_parameters_detector,
    result_set_check_detector,
    expensive_log_statement_detector,
    # implicit_functional_interface_detector,
    literals_first_in_comparison_detector,
    # unused_local_variable_detector
) 

def is_javafx_code(content):
    """
    Detects if the given Java code contains JavaFX or Swing GUI elements.
    Returns True if JavaFX or Swing code is detected, False otherwise.
    """
    content_lower = content.lower()
    
    # Check for JavaFX package imports
    if 'import javafx.' in content or 'import static javafx.' in content:
        return True
    
    # Check for Swing/AWT package imports
    if 'import javax.swing.' in content or 'import java.awt.' in content:
        return True
    
    # Check for @FXML annotation (case-sensitive)
    if '@FXML' in content or '@fxml' in content_lower:
        return True
    
    # Check for JavaFX Application class
    if 'extends Application' in content:
        return True
    
    # Check for Swing class extensions
    swing_extensions = [
        'extends JFrame',
        'extends JDialog',
        'extends JPanel',
        'extends JApplet',
        'extends JWindow',
        'extends javax.swing.JFrame',
        'extends javax.swing.JDialog',
        'extends javax.swing.JPanel',
        'extends javax.swing.JApplet',
        'extends javax.swing.JWindow',
    ]
    
    for extension in swing_extensions:
        if extension in content:
            return True
    
    # Check for common JavaFX class names and methods
    javafx_keywords = [
        'javafx.',  # Any javafx package reference
        'fxmlloader',
        'stage.show',
        'scene(',
        'primarystage',
        'setscene(',
        'getscene(',
        'fxml',
        'borderpane',
        'anchorpane',
        'stackpane',
        'gridpane',
        'flowpane',
        'tilepane',
        'hbox',
        'vbox',
        'imageview',
        'tableview',
        'listview',
        'treeview',
        'scrollpane',
        'splitpane',
        'tabpane',
        'accordion',
        'titledpane',
        'controller',
        'initialize()',
        'observable',
        'property<',
    ]
    
    # Check for common Swing class names and methods
    swing_keywords = [
        'javax.swing.',
        'java.awt.',
        'jframe',
        'jdialog',
        'jpanel',
        'jbutton',
        'jlabel',
        'jtextfield',
        'jtextarea',
        'jcombobox',
        'jlist',
        'jtable',
        'jtree',
        'jmenubar',
        'jtoolbar',
        'jscrollpane',
        'jsplitpane',
        'jtabbedpane',
        'jslider',
        'jspinner',
        'jprogressbar',
        'jcheckbox',
        'jradiobutton',
        'windowbuilder',
        'setdefaultcloseoperation',
        'setcontentpane',
        'getcontentpane',
        'setvisible',
        'pack()',
        'setbounds',
        'setlocation',
        'setsize',
        'addactionlistener',
        'actionlistener',
        'mouselistener',
        'keylistener',
        'windowlistener',
    ]
    
    # Check if any JavaFX or Swing keywords are present
    for keyword in javafx_keywords + swing_keywords:
        if keyword in content_lower:
            return True
    
    return False

def analyze_code(content, filepath):
    smells = []
    source_lines = content.splitlines()
    filename = filepath.split('/')[-1]

    # AST-based analysis
    try:
        tree = javalang.parse.parse(content)
        detectors = [
            complex_method.detect_complex_method_smell,
            feature_envy.detect_feature_envy_smell,
            utility_class_detector.detect_utility_class,
            too_many_methods_detector.detect_too_many_methods,
            too_many_fields_detector.detect_too_many_fields,
            switch_density_detector.detect_switch_density,
            excessive_parameter_list_detector.detect_excessive_parameter_list,
            excessive_imports_detector.detect_excessive_imports,
            cyclomatic_complexity_detector.detect_cyclomatic_complexity,
            private_constructors_final_detector.detect_private_constructors_final,
            unchecked_exceptions_detector.detect_unchecked_exceptions,
            raw_exception_types_detector.detect_raw_exception_types,
            null_pointer_exception_detector.detect_null_pointer_exception,
            nested_if_detector.detect_nested_if,
            reassigning_catch_variables_detector.detect_reassigning_catch_variables,
            reassigning_loop_variables_detector.detect_reassigning_loop_variables,
            reassigning_parameters_detector.detect_reassigning_parameters,
            result_set_check_detector.detect_result_set_check,
            expensive_log_statement_detector.detect_expensive_log_statement,
            # implicit_functional_interface_detector.detect_implicit_functional_interface,
            literals_first_in_comparison_detector.detect_literals_first_in_comparison,
            # unused_local_variable_detector.detect_unused_local_variable
        ]
        for path, node in javalang.ast.walk_tree(tree):
            for detector in detectors:
                result = detector(node, source_lines, filepath, filename)
                if result:
                    smells.extend(result if isinstance(result, list) else [result])
    except javalang.parser.JavaSyntaxError:
        pass  # Skip unparsable files



    return smells

import zipfile

def traverse_zip(zip_data):
    detected_smells = {}
    with zipfile.ZipFile(zip_data, 'r') as zip_ref:
        for file_info in zip_ref.infolist():
            # Skip if the file is in a 'test' directory
            if 'test/' in file_info.filename.lower():
                continue
            if file_info.filename.endswith('.java'):
                with zip_ref.open(file_info) as java_file:
                    try:
                        content = java_file.read().decode('utf-8')
                        
                        # Skip JavaFX files
                        if is_javafx_code(content):
                            continue
                        
                        smells = analyze_code(content, file_info.filename)
                        if smells:
                            detected_smells[file_info.filename] = smells
                    except UnicodeDecodeError:
                        continue  # Skip files that can't be decoded
    return detected_smells
