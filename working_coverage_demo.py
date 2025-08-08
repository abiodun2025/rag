#!/usr/bin/env python3
"""
Working Coverage Demo
Demonstrates code generation and coverage testing with a simple, working example.
"""

import os
import subprocess
import tempfile
import shutil

def create_working_demo():
    """Create a working demo of code generation and coverage testing."""
    temp_dir = tempfile.mkdtemp()
    
    try:
        print("🎭 Working Coverage Demo")
        print("=" * 40)
        print(f"📁 Created temporary directory: {temp_dir}")
        
        # Step 1: Generate simple source code
        print("\n📝 Step 1: Generating source code...")
        source_code = '''
def add(a, b):
    """Add two numbers."""
    return a + b

def subtract(a, b):
    """Subtract two numbers."""
    return a - b

def multiply(a, b):
    """Multiply two numbers."""
    return a * b

def divide(a, b):
    """Divide two numbers with error handling."""
    if b == 0:
        return None
    return a / b

def power(base, exponent):
    """Calculate power with edge case handling."""
    if exponent == 0:
        return 1.0
    elif base == 0 and exponent < 0:
        raise ValueError("Cannot raise 0 to negative power")
    return base ** exponent

def calculate_average(numbers):
    """Calculate average of a list of numbers."""
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)

def main():
    """Main function to demonstrate the calculator."""
    print("Calculator Demo:")
    print(f"2 + 3 = {add(2, 3)}")
    print(f"5 - 2 = {subtract(5, 2)}")
    print(f"4 * 6 = {multiply(4, 6)}")
    print(f"10 / 2 = {divide(10, 2)}")
    print(f"10 / 0 = {divide(10, 0)}")
    print(f"2^3 = {power(2, 3)}")
    print(f"5^0 = {power(5, 0)}")
    print(f"Average of [1,2,3,4,5] = {calculate_average([1,2,3,4,5])}")
    print("✅ Calculator demo completed!")

if __name__ == "__main__":
    main()
'''
        
        source_file = os.path.join(temp_dir, "calculator.py")
        with open(source_file, 'w') as f:
            f.write(source_code)
        
        print(f"✅ Generated: {source_file}")
        
        # Step 2: Generate test code
        print("\n🧪 Step 2: Generating test code...")
        test_code = '''
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from calculator import add, subtract, multiply, divide, power, calculate_average

def test_basic_operations():
    """Test basic calculator operations."""
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
    assert subtract(5, 2) == 3
    assert subtract(0, 5) == -5
    assert multiply(4, 6) == 24
    assert multiply(0, 10) == 0

def test_division():
    """Test division with error handling."""
    assert divide(10, 2) == 5.0
    assert divide(0, 5) == 0.0
    assert divide(10, 0) is None

def test_power():
    """Test power operations."""
    assert power(2, 3) == 8
    assert power(5, 0) == 1.0
    assert power(0, 5) == 0

def test_average():
    """Test average calculation."""
    assert calculate_average([1, 2, 3, 4, 5]) == 3.0
    assert calculate_average([]) == 0
    assert calculate_average([10]) == 10.0

if __name__ == "__main__":
    test_basic_operations()
    test_division()
    test_power()
    test_average()
    print("✅ All tests passed!")
'''
        
        test_file = os.path.join(temp_dir, "test_calculator.py")
        with open(test_file, 'w') as f:
            f.write(test_code)
        
        print(f"✅ Generated: {test_file}")
        
        # Step 3: Run the source code
        print("\n🚀 Step 3: Running source code...")
        source_result = subprocess.run(['python3', 'calculator.py'], 
                                     capture_output=True, text=True, cwd=temp_dir)
        
        if source_result.returncode == 0:
            print("✅ Source code executed successfully")
            print(f"📄 Output: {source_result.stdout.strip()}")
        else:
            print(f"❌ Source code failed: {source_result.stderr}")
            return False
        
        # Step 4: Run tests
        print("\n🧪 Step 4: Running tests...")
        test_result = subprocess.run(['python3', 'test_calculator.py'], 
                                   capture_output=True, text=True, cwd=temp_dir)
        
        if test_result.returncode == 0:
            print("✅ Tests executed successfully")
            print(f"📄 Output: {test_result.stdout.strip()}")
        else:
            print(f"❌ Tests failed: {test_result.stderr}")
            return False
        
        # Step 5: Run coverage analysis
        print("\n📊 Step 5: Running coverage analysis...")
        coverage_result = subprocess.run([
            'python3', '-m', 'coverage', 'run', '--source=calculator', 
            'test_calculator.py'
        ], capture_output=True, text=True, cwd=temp_dir)
        
        if coverage_result.returncode == 0:
            print("✅ Coverage data collected")
            
            # Generate coverage report
            report_result = subprocess.run([
                'python3', '-m', 'coverage', 'report'
            ], capture_output=True, text=True, cwd=temp_dir)
            
            if report_result.returncode == 0:
                print("📊 Coverage Report:")
                print(report_result.stdout)
                
                # Parse and analyze coverage
                coverage_data = parse_coverage_report(report_result.stdout)
                if coverage_data:
                    display_coverage_analysis(coverage_data)
                    generate_suggestions(coverage_data)
                else:
                    print("❌ Failed to parse coverage data")
            else:
                print(f"❌ Failed to generate coverage report: {report_result.stderr}")
        else:
            print(f"❌ Coverage run failed: {coverage_result.stderr}")
        
        print("\n🎉 Demo completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return False
    finally:
        # Cleanup
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            print(f"\n🧹 Cleaned up: {temp_dir}")

def parse_coverage_report(report_output: str) -> dict:
    """Parse coverage report output."""
    try:
        lines = report_output.strip().split('\n')
        for line in lines:
            if 'calculator.py' in line and 'TOTAL' not in line:
                parts = line.split()
                if len(parts) >= 4:
                    total_lines = int(parts[1])
                    missing_lines = int(parts[2])
                    covered_lines = total_lines - missing_lines
                    coverage = (covered_lines / total_lines) * 100 if total_lines > 0 else 0
                    
                    return {
                        'total_lines': total_lines,
                        'covered_lines': covered_lines,
                        'missing_lines': missing_lines,
                        'coverage': round(coverage, 1)
                    }
        return None
    except Exception as e:
        print(f"Error parsing coverage report: {e}")
        return None

def display_coverage_analysis(coverage_data: dict):
    """Display coverage analysis results."""
    print(f"\n📈 Coverage Analysis:")
    print(f"   📄 Total Lines: {coverage_data['total_lines']}")
    print(f"   ✅ Covered Lines: {coverage_data['covered_lines']}")
    print(f"   ❌ Missing Lines: {coverage_data['missing_lines']}")
    print(f"   📊 Coverage: {coverage_data['coverage']}%")
    
    # Coverage status
    coverage = coverage_data['coverage']
    if coverage >= 90:
        print("   🎉 Excellent coverage!")
    elif coverage >= 80:
        print("   ✅ Good coverage")
    elif coverage >= 70:
        print("   ⚠️ Moderate coverage")
    else:
        print("   🔴 Low coverage - needs improvement")

def generate_suggestions(coverage_data: dict):
    """Generate improvement suggestions based on coverage."""
    print(f"\n💡 Improvement Suggestions:")
    
    coverage = coverage_data['coverage']
    missing_lines = coverage_data['missing_lines']
    
    suggestions = []
    
    if coverage < 80:
        suggestions.append("🔴 High Priority: Add more test cases to improve coverage")
    
    if missing_lines > 0:
        suggestions.append(f"🟡 Medium Priority: {missing_lines} lines need test coverage")
    
    if coverage < 90:
        suggestions.append("🟢 Low Priority: Consider edge case testing")
    
    # Specific suggestions
    suggestions.append("💡 Suggestion: Test error handling paths")
    suggestions.append("💡 Suggestion: Add integration tests for complex scenarios")
    suggestions.append("💡 Suggestion: Test boundary conditions")
    suggestions.append("💡 Suggestion: Add performance tests for large datasets")
    
    for i, suggestion in enumerate(suggestions, 1):
        print(f"   {i}. {suggestion}")

def main():
    """Main function to run the demo."""
    success = create_working_demo()
    if success:
        print("\n🎉 Working Coverage Demo completed successfully!")
    else:
        print("\n❌ Working Coverage Demo failed!")

if __name__ == "__main__":
    main()
