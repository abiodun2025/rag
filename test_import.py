#!/usr/bin/env python3
"""
Test script to check if the improved code generator can be imported and used
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
    
    result = generator.generate_code("me a kotlin function that add two numbers 4 and 10", "kotlin")
    print("✅ Code generation successful")
    print(f"📝 Result length: {len(result)}")
    print(f"📝 First 100 chars: {result[:100]}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc() 