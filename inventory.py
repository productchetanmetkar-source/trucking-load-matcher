#!/usr/bin/env python3
"""
System Inventory Script - Create comprehensive documentation of existing codebase
This will serve as our RAG reference for writing compatible code
"""

import os
import ast
import inspect
from typing import Dict, List, Any
import importlib.util

def extract_class_info(filepath: str) -> Dict[str, Any]:
    """Extract class definitions, methods, and fields from a Python file"""
    
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        tree = ast.parse(content)
        classes_info = {}
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_info = {
                    'name': node.name,
                    'fields': [],
                    'methods': [],
                    'enums': [],
                    'base_classes': [base.id if hasattr(base, 'id') else str(base) for base in node.bases]
                }
                
                # Extract class body
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        # Method
                        args = [arg.arg for arg in item.args.args if arg.arg != 'self']
                        class_info['methods'].append({
                            'name': item.name,
                            'args': args,
                            'is_private': item.name.startswith('_')
                        })
                    
                    elif isinstance(item, ast.AnnAssign) and hasattr(item.target, 'id'):
                        # Field with type annotation
                        field_name = item.target.id
                        field_type = ast.unparse(item.annotation) if hasattr(ast, 'unparse') else str(item.annotation)
                        
                        # Check if it has a default value
                        default_value = None
                        if item.value:
                            try:
                                default_value = ast.literal_eval(item.value)
                            except:
                                default_value = "complex_default"
                        
                        class_info['fields'].append({
                            'name': field_name,
                            'type': field_type,
                            'default': default_value
                        })
                    
                    elif isinstance(item, ast.Assign):
                        # Regular assignment
                        for target in item.targets:
                            if hasattr(target, 'id'):
                                class_info['fields'].append({
                                    'name': target.id,
                                    'type': 'unknown',
                                    'default': 'assigned'
                                })
                
                classes_info[node.name] = class_info
        
        return classes_info
        
    except Exception as e:
        return {'error': str(e)}

def extract_function_info(filepath: str) -> List[Dict[str, Any]]:
    """Extract standalone functions from a Python file"""
    
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        tree = ast.parse(content)
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check if it's a top-level function (not inside a class)
                parent = getattr(node, 'parent', None)
                if not isinstance(parent, ast.ClassDef):
                    args = [arg.arg for arg in node.args.args]
                    functions.append({
                        'name': node.name,
                        'args': args,
                        'is_private': node.name.startswith('_')
                    })
        
        return functions
        
    except Exception as e:
        return [{'error': str(e)}]

def scan_directory(directory: str) -> Dict[str, Any]:
    """Scan entire project directory and extract all entities"""
    
    inventory = {
        'models': {},
        'agents': {},
        'utils': {},
        'knowledge': {},
        'tests': {},
        'config': {},
        'other': {}
    }
    
    for root, dirs, files in os.walk(directory):
        # Skip virtual environment and hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'venv']
        
        for file in files:
            if file.endswith('.py') and not file.startswith('.'):
                filepath = os.path.join(root, file)
                relative_path = os.path.relpath(filepath, directory)
                
                print(f"📁 Scanning: {relative_path}")
                
                # Extract classes and functions
                classes = extract_class_info(filepath)
                functions = extract_function_info(filepath)
                
                file_info = {
                    'path': relative_path,
                    'classes': classes,
                    'functions': functions
                }
                
                # Categorize by directory
                if 'models/' in relative_path:
                    inventory['models'][file] = file_info
                elif 'agents/' in relative_path:
                    inventory['agents'][file] = file_info
                elif 'utils/' in relative_path:
                    inventory['utils'][file] = file_info
                elif 'knowledge/' in relative_path:
                    inventory['knowledge'][file] = file_info
                elif 'test' in relative_path.lower():
                    inventory['tests'][file] = file_info
                else:
                    inventory['other'][file] = file_info
    
    return inventory

def generate_compatibility_guide(inventory: Dict[str, Any]) -> str:
    """Generate a compatibility guide for writing new code"""
    
    guide = """# TRUCKING LOAD MATCHER - SYSTEM COMPATIBILITY GUIDE
## Auto-generated from existing codebase

This document serves as the definitive reference for writing compatible code.
ALL new code must follow these exact interfaces and data structures.

"""
    
    # Models section
    guide += "## MODELS (Data Structures)\n\n"
    
    for filename, file_info in inventory['models'].items():
        guide += f"### {filename}\n"
        guide += f"**File**: `{file_info['path']}`\n\n"
        
        for class_name, class_info in file_info['classes'].items():
            guide += f"#### Class: {class_name}\n"
            if class_info.get('base_classes'):
                guide += f"**Inherits from**: {', '.join(class_info['base_classes'])}\n"
            
            guide += "**Fields**:\n"
            for field in class_info['fields']:
                default_info = f" = {field['default']}" if field['default'] is not None else ""
                guide += f"- `{field['name']}: {field['type']}`{default_info}\n"
            
            guide += "**Methods**:\n"
            for method in class_info['methods']:
                args_str = ', '.join(method['args'])
                guide += f"- `{method['name']}({args_str})`\n"
            
            guide += "\n"
        
        guide += "---\n\n"
    
    # Agents section
    guide += "## AGENTS (Processing Logic)\n\n"
    
    for filename, file_info in inventory['agents'].items():
        guide += f"### {filename}\n"
        guide += f"**File**: `{file_info['path']}`\n\n"
        
        for class_name, class_info in file_info['classes'].items():
            guide += f"#### Class: {class_name}\n"
            
            guide += "**Key Methods**:\n"
            for method in class_info['methods']:
                if not method['is_private']:  # Only show public methods
                    args_str = ', '.join(method['args'])
                    guide += f"- `{method['name']}({args_str})`\n"
            
            guide += "\n"
        
        guide += "---\n\n"
    
    # Utils section
    guide += "## UTILITIES\n\n"
    
    for filename, file_info in inventory['utils'].items():
        guide += f"### {filename}\n"
        guide += f"**File**: `{file_info['path']}`\n\n"
        
        # Show classes
        for class_name, class_info in file_info['classes'].items():
            guide += f"#### Class: {class_name}\n"
            public_methods = [m for m in class_info['methods'] if not m['is_private']]
            for method in public_methods:
                args_str = ', '.join(method['args'])
                guide += f"- `{method['name']}({args_str})`\n"
            guide += "\n"
        
        # Show functions
        if file_info['functions']:
            guide += "**Functions**:\n"
            for func in file_info['functions']:
                if not func['is_private']:
                    args_str = ', '.join(func['args'])
                    guide += f"- `{func['name']}({args_str})`\n"
        
        guide += "---\n\n"
    
    # Critical interfaces
    guide += """## CRITICAL INTERFACES FOR MAIN.PY

Based on the codebase scan, any main.py orchestrator MUST:

### Entity Extraction Interface
```python
# Your EntityExtractionAgent expects:
extracted_entities = entity_agent.extract_entities(transcript_object)
# Where transcript_object has .turns attribute
```

### Load Matching Interface  
```python
# Your LoadMatchingAgent expects:
load_matches = load_agent.match_loads(extracted_entities, available_loads)
```

### Data Model Requirements
- ExtractedEntities: Use EXACT field names from models/entities_model.py
- Load: Use EXACT field names from models/load_model.py  
- Transcript: Must have .turns attribute with ConversationTurn objects

### Import Statements (Copy exactly)
```python
from agents.entity_extraction_agent import EntityExtractionAgent
from agents.load_matching_agent import LoadMatchingAgent
from models.transcript_model import Transcript, ConversationTurn
from models.load_model import Load, LoadStatus
from models.entities_model import ExtractedEntities, TruckType
```

"""
    
    return guide

def main():
    """Generate comprehensive system inventory"""
    
    print("🔍 TRUCKING LOAD MATCHER - SYSTEM INVENTORY")
    print("=" * 60)
    
    # Scan current directory
    current_dir = "."
    
    print(f"📂 Scanning directory: {os.path.abspath(current_dir)}")
    
    inventory = scan_directory(current_dir)
    
    # Generate compatibility guide
    guide = generate_compatibility_guide(inventory)
    
    # Save to file
    with open("SYSTEM_COMPATIBILITY_GUIDE.md", "w") as f:
        f.write(guide)
    
    print(f"\n✅ Generated: SYSTEM_COMPATIBILITY_GUIDE.md")
    
    # Print summary
    print(f"\n📊 INVENTORY SUMMARY:")
    print(f"   Models: {len(inventory['models'])} files")
    print(f"   Agents: {len(inventory['agents'])} files") 
    print(f"   Utils: {len(inventory['utils'])} files")
    print(f"   Knowledge: {len(inventory['knowledge'])} files")
    print(f"   Tests: {len(inventory['tests'])} files")
    print(f"   Other: {len(inventory['other'])} files")
    
    # Show key entities found
    print(f"\n🎯 KEY ENTITIES DISCOVERED:")
    
    for category, files in inventory.items():
        if category in ['models', 'agents'] and files:
            print(f"\n{category.upper()}:")
            for filename, file_info in files.items():
                for class_name in file_info['classes'].keys():
                    print(f"   • {class_name} (in {filename})")
    
    print(f"\n📖 Use SYSTEM_COMPATIBILITY_GUIDE.md as reference for all new code!")

if __name__ == "__main__":
    main()