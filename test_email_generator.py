#!/usr/bin/env python3
"""
Test script for email notification code generation
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.getcwd())

try:
    from improved_code_generator import ImprovedCodeGenerator
    print("✅ Import successful")
    
    generator = ImprovedCodeGenerator()
    print("✅ Generator created")
    
    result = generator.generate_code("write me function that send email notification in kotlin", "kotlin", True, True)
    print("✅ Code generation successful")
    print(f"📝 Result length: {len(result)}")
    print("📝 Generated Code:")
    print("=" * 50)
    print(result)
    print("=" * 50)
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc() 