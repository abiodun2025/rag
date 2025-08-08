#!/usr/bin/env python3
"""
Demo: Code Generation and Coverage Testing
Demonstrates generating code, writing tests, and analyzing coverage.
"""

import os
import subprocess
import tempfile
import shutil
from pathlib import Path

class CodeCoverageDemo:
    """Demo class for code generation and coverage testing."""
    
    def __init__(self):
        self.temp_dir = None
        
    def run_demo(self):
        """Run the complete demo."""
        print("🎭 Code Generation and Coverage Demo")
        print("=" * 50)
        
        try:
            # Create temporary directory
            self.temp_dir = tempfile.mkdtemp()
            print(f"📁 Created temporary directory: {self.temp_dir}")
            
            # Step 1: Generate source code
            print("\n📝 Step 1: Generating source code...")
            source_file = self._generate_source_code()
            print(f"✅ Generated: {source_file}")
            
            # Step 2: Generate test code
            print("\n🧪 Step 2: Generating test code...")
            test_file = self._generate_test_code()
            print(f"✅ Generated: {test_file}")
            
            # Step 3: Run tests with coverage
            print("\n📊 Step 3: Running tests with coverage...")
            coverage_result = self._run_coverage_analysis()
            
            if coverage_result:
                print("✅ Coverage analysis completed")
                self._display_coverage_results(coverage_result)
            else:
                print("❌ Coverage analysis failed")
            
            # Step 4: Generate suggestions
            print("\n💡 Step 4: Generating improvement suggestions...")
            suggestions = self._generate_suggestions(coverage_result)
            self._display_suggestions(suggestions)
            
            print("\n🎉 Demo completed successfully!")
            
        except Exception as e:
            print(f"❌ Demo failed: {e}")
        finally:
            # Cleanup
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                print(f"\n🧹 Cleaned up: {self.temp_dir}")
    
    def _generate_source_code(self) -> str:
        """Generate sample source code."""
        source_code = '''
#!/usr/bin/env python3
"""
Sample source code for coverage testing.
"""

import math
from typing import List, Optional, Dict

class DataProcessor:
    """A data processing class with various methods to test coverage."""
    
    def __init__(self):
        self.data = []
        self.processed_count = 0
    
    def add_data(self, item: any) -> bool:
        """Add an item to the data list."""
        if item is None:
            return False
        
        self.data.append(item)
        return True
    
    def remove_data(self, item: any) -> bool:
        """Remove an item from the data list."""
        if item in self.data:
            self.data.remove(item)
            return True
        return False
    
    def process_data(self, operation: str) -> Optional[List]:
        """Process data based on operation type."""
        if not self.data:
            return None
        
        if operation == "sort":
            # Handle mixed types by converting to strings for comparison
            result = sorted(self.data, key=lambda x: str(x))
        elif operation == "reverse":
            result = list(reversed(self.data))
        elif operation == "unique":
            result = list(set(self.data))
        elif operation == "filter":
            # Filter out None values
            result = [item for item in self.data if item is not None]
        else:
            return None
        
        self.processed_count += 1
        return result
    
    def calculate_statistics(self) -> Dict[str, float]:
        """Calculate basic statistics on numeric data."""
        numeric_data = [item for item in self.data if isinstance(item, (int, float))]
        
        if not numeric_data:
            return {}
        
        stats = {
            "count": len(numeric_data),
            "sum": sum(numeric_data),
            "mean": sum(numeric_data) / len(numeric_data),
            "min": min(numeric_data),
            "max": max(numeric_data)
        }
        
        # Calculate standard deviation
        mean = stats["mean"]
        variance = sum((x - mean) ** 2 for x in numeric_data) / len(numeric_data)
        stats["std_dev"] = math.sqrt(variance)
        
        return stats
    
    def get_data_summary(self) -> Dict[str, any]:
        """Get a summary of the current data."""
        return {
            "total_items": len(self.data),
            "processed_count": self.processed_count,
            "data_types": list(set(type(item).__name__ for item in self.data)),
            "has_numeric": any(isinstance(item, (int, float)) for item in self.data)
        }
    
    def clear_data(self):
        """Clear all data."""
        self.data.clear()
        self.processed_count = 0

def main():
    """Main function to demonstrate the DataProcessor."""
    processor = DataProcessor()
    
    # Add some data
    processor.add_data(1)
    processor.add_data(2)
    processor.add_data(3)
    processor.add_data("hello")
    processor.add_data(None)
    
    # Process data
    sorted_data = processor.process_data("sort")
    print(f"Sorted data: {sorted_data}")
    
    # Calculate statistics
    stats = processor.calculate_statistics()
    print(f"Statistics: {stats}")
    
    # Get summary
    summary = processor.get_data_summary()
    print(f"Summary: {summary}")

if __name__ == "__main__":
    main()
'''
        
        source_file = os.path.join(self.temp_dir, "data_processor.py")
        with open(source_file, 'w') as f:
            f.write(source_code)
        
        return source_file
    
    def _generate_test_code(self) -> str:
        """Generate test code for the source code."""
        test_code = '''
#!/usr/bin/env python3
"""
Test code for DataProcessor class.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_processor import DataProcessor

def test_basic_operations():
    """Test basic data operations."""
    processor = DataProcessor()
    
    # Test adding data
    assert processor.add_data(1) == True
    assert processor.add_data("test") == True
    assert processor.add_data(None) == False
    
    # Test removing data
    assert processor.remove_data(1) == True
    assert processor.remove_data(999) == False

def test_data_processing():
    """Test data processing operations."""
    processor = DataProcessor()
    
    # Add test data
    processor.add_data(3)
    processor.add_data(1)
    processor.add_data(2)
    processor.add_data("b")
    processor.add_data("a")
    
    # Test sorting
    sorted_data = processor.process_data("sort")
    assert len(sorted_data) == 5
    assert 1 in sorted_data
    assert 2 in sorted_data
    assert 3 in sorted_data
    assert "a" in sorted_data
    assert "b" in sorted_data
    
    # Test reverse
    reversed_data = processor.process_data("reverse")
    assert len(reversed_data) == 5
    assert reversed_data[0] == "b"  # Last item becomes first
    assert reversed_data[-1] == 1   # First item becomes last
    
    # Test unique
    processor.add_data(1)  # Add duplicate
    unique_data = processor.process_data("unique")
    assert len(unique_data) == 5  # Should have 5 unique items
    
    # Test filter
    processor.add_data(None)
    filtered_data = processor.process_data("filter")
    assert None not in filtered_data
    
    # Test invalid operation
    invalid_result = processor.process_data("invalid")
    assert invalid_result is None

def test_statistics():
    """Test statistics calculation."""
    processor = DataProcessor()
    
    # Test with no numeric data
    stats = processor.calculate_statistics()
    assert stats == {}
    
    # Test with numeric data
    processor.add_data(1)
    processor.add_data(2)
    processor.add_data(3)
    
    stats = processor.calculate_statistics()
    assert stats["count"] == 3
    assert stats["sum"] == 6
    assert stats["mean"] == 2.0
    assert stats["min"] == 1
    assert stats["max"] == 3
    assert "std_dev" in stats

def test_summary():
    """Test data summary functionality."""
    processor = DataProcessor()
    
    # Test empty summary
    summary = processor.get_data_summary()
    assert summary["total_items"] == 0
    assert summary["processed_count"] == 0
    
    # Test with data
    processor.add_data(1)
    processor.add_data("test")
    processor.process_data("sort")
    
    summary = processor.get_data_summary()
    assert summary["total_items"] == 2
    assert summary["processed_count"] == 1
    assert "int" in summary["data_types"]
    assert "str" in summary["data_types"]
    assert summary["has_numeric"] == True

def test_clear_data():
    """Test clearing data."""
    processor = DataProcessor()
    
    processor.add_data(1)
    processor.add_data(2)
    processor.process_data("sort")
    
    processor.clear_data()
    
    summary = processor.get_data_summary()
    assert summary["total_items"] == 0
    assert summary["processed_count"] == 0

if __name__ == "__main__":
    test_basic_operations()
    test_data_processing()
    test_statistics()
    test_summary()
    test_clear_data()
    print("✅ All tests passed!")
'''
        
        test_file = os.path.join(self.temp_dir, "test_data_processor.py")
        with open(test_file, 'w') as f:
            f.write(test_code)
        
        return test_file
    
    def _run_coverage_analysis(self) -> dict:
        """Run coverage analysis on the generated code."""
        try:
            # Install coverage if needed
            try:
                subprocess.run(['python3', '-m', 'coverage', '--version'], 
                             capture_output=True, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("📦 Installing coverage...")
                subprocess.run(['pip3', 'install', 'coverage'], check=True)
            
            # First run the test to make sure it works
            test_result = subprocess.run(['python3', 'test_data_processor.py'], 
                                       capture_output=True, text=True, cwd=self.temp_dir)
            
            if test_result.returncode != 0:
                print(f"❌ Test execution failed: {test_result.stderr}")
                return None
            
            # Run tests with coverage
            result = subprocess.run([
                'python3', '-m', 'coverage', 'run', '--source=data_processor', 
                'test_data_processor.py'
            ], capture_output=True, text=True, cwd=self.temp_dir)
            
            if result.returncode == 0:
                # Generate coverage report
                report_result = subprocess.run([
                    'python3', '-m', 'coverage', 'report'
                ], capture_output=True, text=True, cwd=self.temp_dir)
                
                if report_result.returncode == 0:
                    return self._parse_coverage_report(report_result.stdout)
                else:
                    print(f"❌ Failed to generate coverage report: {report_result.stderr}")
            else:
                print(f"❌ Coverage run failed: {result.stderr}")
            
            return None
            
        except Exception as e:
            print(f"Error in coverage analysis: {e}")
            return None
    
    def _parse_coverage_report(self, report_output: str) -> dict:
        """Parse coverage report output."""
        try:
            lines = report_output.strip().split('\n')
            for line in lines:
                if 'data_processor.py' in line and 'TOTAL' not in line:
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
                            'coverage': round(coverage, 1),
                            'raw_report': report_output
                        }
            return None
        except Exception as e:
            print(f"Error parsing coverage report: {e}")
            return None
    
    def _display_coverage_results(self, coverage_data: dict):
        """Display coverage results."""
        print(f"\n📊 Coverage Results:")
        print(f"   📄 Total Lines: {coverage_data['total_lines']}")
        print(f"   ✅ Covered Lines: {coverage_data['covered_lines']}")
        print(f"   ❌ Missing Lines: {coverage_data['missing_lines']}")
        print(f"   📈 Coverage: {coverage_data['coverage']}%")
        
        # Display coverage status
        if coverage_data['coverage'] >= 90:
            print("   🎉 Excellent coverage!")
        elif coverage_data['coverage'] >= 80:
            print("   ✅ Good coverage")
        elif coverage_data['coverage'] >= 70:
            print("   ⚠️ Moderate coverage")
        else:
            print("   🔴 Low coverage - needs improvement")
    
    def _generate_suggestions(self, coverage_data: dict) -> list:
        """Generate improvement suggestions based on coverage."""
        suggestions = []
        
        if not coverage_data:
            suggestions.append("❌ Unable to analyze coverage - check test execution")
            return suggestions
        
        coverage = coverage_data['coverage']
        missing_lines = coverage_data['missing_lines']
        
        if coverage < 80:
            suggestions.append("🔴 High Priority: Add more test cases to improve coverage")
        
        if missing_lines > 0:
            suggestions.append(f"🟡 Medium Priority: {missing_lines} lines need test coverage")
        
        if coverage < 90:
            suggestions.append("🟢 Low Priority: Consider edge case testing")
        
        # Specific suggestions based on typical uncovered areas
        suggestions.append("💡 Suggestion: Test error handling paths")
        suggestions.append("💡 Suggestion: Add integration tests for complex scenarios")
        suggestions.append("💡 Suggestion: Test boundary conditions")
        suggestions.append("💡 Suggestion: Add performance tests for large datasets")
        
        return suggestions
    
    def _display_suggestions(self, suggestions: list):
        """Display improvement suggestions."""
        print(f"\n💡 Improvement Suggestions ({len(suggestions)} total):")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"   {i}. {suggestion}")

def main():
    """Main function to run the demo."""
    demo = CodeCoverageDemo()
    demo.run_demo()

if __name__ == "__main__":
    main()
