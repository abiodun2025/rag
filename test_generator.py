#!/usr/bin/env python3
"""
Test script for the improved code generator
"""

from improved_code_generator import ImprovedCodeGenerator

def test_kotlin_generation():
    generator = ImprovedCodeGenerator()
    
    # Test the specific request that was failing
    instructions = "me a kotlin function that add two numbers 4 and 10"
    
    print("Testing Kotlin code generation...")
    print(f"Instructions: {instructions}")
    print("\n" + "="*50)
    
    result = generator.generate_code(instructions, 'kotlin')
    print(result)
    print("="*50)

if __name__ == "__main__":
    test_kotlin_generation() 