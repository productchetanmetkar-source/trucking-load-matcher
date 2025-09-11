#!/usr/bin/env python3
"""
Debug script to check what's available in the main.py file
"""

import sys
import os
import importlib.util

def check_main_py():
    """Check what's actually in main.py"""
    
    main_path = "main.py"
    
    if not os.path.exists(main_path):
        print(f"❌ {main_path} not found!")
        return
    
    print(f"📁 Found {main_path}")
    print("=" * 50)
    
    # Read and show first few lines
    with open(main_path, 'r') as f:
        lines = f.readlines()
    
    print("📋 First 20 lines of main.py:")
    for i, line in enumerate(lines[:20], 1):
        print(f"{i:2d}: {line.rstrip()}")
    
    print("\n" + "=" * 50)
    
    # Try to import and see what's available
    try:
        spec = importlib.util.spec_from_file_location("main", main_path)
        main_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(main_module)
        
        print("✅ Successfully imported main.py")
        print("\n🔍 Available attributes:")
        
        for attr in dir(main_module):
            if not attr.startswith('_'):
                obj = getattr(main_module, attr)
                obj_type = type(obj).__name__
                print(f"   • {attr} ({obj_type})")
                
                # If it's a class, show its methods
                if obj_type == 'type':
                    methods = [m for m in dir(obj) if not m.startswith('_')]
                    if methods:
                        print(f"     Methods: {', '.join(methods[:5])}")
                        if len(methods) > 5:
                            print(f"     ... and {len(methods) - 5} more")
        
        # Check specifically for matcher-related classes
        matcher_classes = [attr for attr in dir(main_module) 
                          if 'match' in attr.lower() or 'truck' in attr.lower()]
        
        if matcher_classes:
            print(f"\n🎯 Found matcher-related classes: {matcher_classes}")
        else:
            print(f"\n❌ No matcher classes found")
            
    except Exception as e:
        print(f"❌ Failed to import main.py: {e}")
        print(f"   Error type: {type(e).__name__}")

def check_other_files():
    """Check for matcher classes in other files"""
    
    print("\n" + "=" * 50)
    print("🔍 Searching for matcher classes in other files...")
    
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.py') and not file.startswith('.'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r') as f:
                        content = f.read()
                        
                    if 'class' in content and ('Matcher' in content or 'matcher' in content):
                        print(f"📁 {filepath}:")
                        
                        # Find class definitions
                        lines = content.split('\n')
                        for i, line in enumerate(lines):
                            if line.strip().startswith('class') and ('Matcher' in line or 'matcher' in line):
                                print(f"   Line {i+1}: {line.strip()}")
                
                except Exception:
                    pass  # Skip files we can't read

def main():
    """Run all checks"""
    print("🔧 Debugging import issues...")
    print("=" * 50)
    
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    check_main_py()
    check_other_files()
    
    print("\n" + "=" * 50)
    print("💡 Recommendations:")
    print("   1. Check the class name in main.py")
    print("   2. Update app.py import to match actual class name")
    print("   3. Or create the missing TruckingLoadMatcher class")

if __name__ == "__main__":
    main()