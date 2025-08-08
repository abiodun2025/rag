#!/usr/bin/env python3
"""
Simple Coverage Test
"""

import os
import subprocess
import tempfile
import shutil

def create_simple_test():
    """Create a simple test to verify coverage works."""
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Create a simple source file
        source_code = '''
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        return None
    return a / b
'''
        
        source_file = os.path.join(temp_dir, "math_ops.py")
        with open(source_file, 'w') as f:
            f.write(source_code)
        
        # Create a simple test file
        test_code = '''
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from math_ops import add, subtract, multiply, divide

def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0

def test_subtract():
    assert subtract(5, 2) == 3
    assert subtract(0, 5) == -5

def test_multiply():
    assert multiply(4, 6) == 24
    assert multiply(0, 10) == 0

def test_divide():
    assert divide(10, 2) == 5.0
    assert divide(0, 5) == 0.0
    assert divide(10, 0) is None

if __name__ == "__main__":
    test_add()
    test_subtract()
    test_multiply()
    test_divide()
    print("✅ All tests passed!")
'''
        
        test_file = os.path.join(temp_dir, "test_math_ops.py")
        with open(test_file, 'w') as f:
            f.write(test_code)
        
        print(f"📁 Created test files in: {temp_dir}")
        print(f"📄 Source: {source_file}")
        print(f"🧪 Test: {test_file}")
        
        # Run tests with coverage
        print("\n🧪 Running tests with coverage...")
        
        # First, run the test to make sure it works
        test_result = subprocess.run(['python3', 'test_math_ops.py'], 
                                   capture_output=True, text=True, cwd=temp_dir)
        
        print(f"Test result: {test_result.returncode}")
        print(f"Test output: {test_result.stdout}")
        if test_result.stderr:
            print(f"Test error: {test_result.stderr}")
        
        if test_result.returncode == 0:
            # Now run with coverage
            coverage_result = subprocess.run([
                'python3', '-m', 'coverage', 'run', '--source=math_ops', 
                'test_math_ops.py'
            ], capture_output=True, text=True, cwd=temp_dir)
            
            print(f"Coverage run result: {coverage_result.returncode}")
            if coverage_result.stderr:
                print(f"Coverage error: {coverage_result.stderr}")
            
            if coverage_result.returncode == 0:
                # Generate coverage report
                report_result = subprocess.run([
                    'python3', '-m', 'coverage', 'report'
                ], capture_output=True, text=True, cwd=temp_dir)
                
                print(f"Report result: {report_result.returncode}")
                print(f"Coverage report:\n{report_result.stdout}")
                if report_result.stderr:
                    print(f"Report error: {report_result.stderr}")
                
                return True
            else:
                print("❌ Coverage run failed")
                return False
        else:
            print("❌ Test execution failed")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        # Cleanup
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            print(f"🧹 Cleaned up: {temp_dir}")

if __name__ == "__main__":
    print("🧪 Simple Coverage Test")
    print("=" * 30)
    success = create_simple_test()
    if success:
        print("✅ Coverage test completed successfully!")
    else:
        print("❌ Coverage test failed!")
