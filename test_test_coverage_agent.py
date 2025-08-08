#!/usr/bin/env python3
"""
Test file for Test Coverage & Suggestions Agent

This file demonstrates the agent's capabilities and provides test cases.
"""

import sys
import unittest
from agent.test_coverage_agent import TestCoverageAgent, CoverageData, TestSuggestion

class TestTestCoverageAgent(unittest.TestCase):
    """Test cases for TestCoverageAgent."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.agent = TestCoverageAgent()
    
    def test_language_detection(self):
        """Test language detection from file extensions."""
        test_cases = [
            ('src/main.java', 'java'),
            ('app/User.kt', 'kt'),
            ('components/Button.js', 'js'),
            ('utils/helper.ts', 'ts'),
            ('main.py', 'py'),
            ('server.go', 'go'),
            ('unknown.xyz', 'unknown')
        ]
        
        for file_path, expected_language in test_cases:
            with self.subTest(file_path=file_path):
                detected = self.agent._detect_language(file_path)
                self.assertEqual(detected, expected_language)
    
    def test_line_classification(self):
        """Test line type classification."""
        test_cases = [
            ('if user is None:', 'edge_case'),
            ('return None', 'control_flow'),
            ('except ValueError:', 'error_handling'),
            ('if age >= 18:', 'boundary'),
            ('user = None', 'null_check'),
            ('print("Hello")', 'general')
        ]
        
        for code_line, expected_type in test_cases:
            with self.subTest(code_line=code_line):
                detected_type = self.agent._classify_line_type(code_line, 'py')
                self.assertEqual(detected_type, expected_type)
    
    def test_suggestion_generation(self):
        """Test test suggestion generation."""
        # Create mock coverage data
        coverage_data = CoverageData(
            total_lines=10,
            covered_lines=5,
            coverage_percentage=50.0,
            uncovered_lines=[6, 7, 8, 9, 10],
            file_path='test_file.py',
            language='py'
        )
        
        # Create a test file
        test_content = '''def calculate_tax(income, age):
    """Calculate tax based on income and age."""
    if income <= 0:
        return 0
    
    if age < 18:
        return income * 0.05
    
    if age >= 65:
        return income * 0.08
    
    return income * 0.10

def validate_input(data):
    """Validate input data."""
    if data is None:
        return False
    
    if len(data) == 0:
        return False
    
    return True
'''
        
        with open('test_file.py', 'w') as f:
            f.write(test_content)
        
        try:
            # Generate suggestions
            suggestions = self.agent._generate_test_suggestions(
                coverage_data, 'test_file.py', 'py'
            )
            
            # Verify suggestions were generated
            self.assertGreater(len(suggestions), 0)
            
            # Check suggestion structure
            for suggestion in suggestions:
                self.assertIsInstance(suggestion, TestSuggestion)
                self.assertIn(suggestion.priority, ['high', 'medium', 'low'])
                self.assertIn(suggestion.suggestion_type, [
                    'edge_case', 'boundary', 'null_check', 'error_handling', 
                    'control_flow', 'general'
                ])
                
        finally:
            # Clean up
            import os
            if os.path.exists('test_file.py'):
                os.remove('test_file.py')
    
    def test_coverage_report_generation(self):
        """Test coverage report generation."""
        # Create mock coverage data
        coverage_data = [
            CoverageData(
                total_lines=20,
                covered_lines=15,
                coverage_percentage=75.0,
                uncovered_lines=[16, 17, 18, 19, 20],
                file_path='file1.py',
                language='py'
            ),
            CoverageData(
                total_lines=10,
                covered_lines=5,
                coverage_percentage=50.0,
                uncovered_lines=[6, 7, 8, 9, 10],
                file_path='file2.py',
                language='py'
            )
        ]
        
        # Create mock suggestions
        suggestions = [
            TestSuggestion(
                file_path='file1.py',
                line_number=16,
                suggestion_type='edge_case',
                description='Add test case for edge condition',
                code_snippet='if value > 100:',
                priority='medium'
            ),
            TestSuggestion(
                file_path='file2.py',
                line_number=6,
                suggestion_type='null_check',
                description='Add test case for null input',
                code_snippet='if data is None:',
                priority='high'
            )
        ]
        
        # Generate report
        report = self.agent._generate_coverage_report(coverage_data, suggestions)
        
        # Verify report structure
        self.assertIn('overall_coverage', report)
        self.assertIn('file_coverage', report)
        self.assertIn('suggestions', report)
        self.assertIn('recommendations', report)
        self.assertIn('timestamp', report)
        
        # Verify overall coverage calculation
        overall = report['overall_coverage']
        self.assertEqual(overall['total_lines'], 30)
        self.assertEqual(overall['covered_lines'], 20)
        self.assertAlmostEqual(overall['percentage'], 66.67, places=1)
        
        # Verify suggestions count
        suggestions_data = report['suggestions']
        self.assertEqual(suggestions_data['total'], 2)
        self.assertEqual(suggestions_data['high_priority'], 1)
        self.assertEqual(suggestions_data['medium_priority'], 1)
    
    def test_recommendations_generation(self):
        """Test recommendations generation."""
        # Test low coverage
        low_coverage_suggestions = [
            TestSuggestion('file.py', 1, 'null_check', 'Test null', '', 'high'),
            TestSuggestion('file.py', 2, 'edge_case', 'Test edge', '', 'high')
        ]
        
        recommendations = self.agent._generate_recommendations(30.0, low_coverage_suggestions)
        self.assertIn('Critical: Coverage is below 50%', recommendations[0])
        self.assertIn('Focus on 2 high-priority test suggestions', recommendations[1])
        
        # Test good coverage
        good_coverage_suggestions = [
            TestSuggestion('file.py', 1, 'general', 'Minor test', '', 'low')
        ]
        
        recommendations = self.agent._generate_recommendations(85.0, good_coverage_suggestions)
        self.assertIn('Good coverage!', recommendations[0])

def run_demo():
    """Run a demonstration of the Test Coverage Agent."""
    print("🧪 Test Coverage Agent Demo")
    print("=" * 50)
    
    agent = TestCoverageAgent()
    
    # Create a sample file with various code patterns
    sample_code = '''def process_user_data(user_data, age, is_premium=False):
    """Process user data with various validation and business logic."""
    
    # Null checks
    if user_data is None:
        return None
    
    if not user_data:
        return {}
    
    # Boundary conditions
    if age < 0 or age > 150:
        raise ValueError("Invalid age")
    
    if age < 18:
        return {"status": "minor", "data": user_data}
    
    # Edge cases
    if age == 18:
        return {"status": "new_adult", "data": user_data}
    
    # Business logic
    if is_premium and age >= 65:
        return {"status": "senior_premium", "data": user_data, "discount": 0.15}
    
    if is_premium:
        return {"status": "premium", "data": user_data, "discount": 0.10}
    
    # Error handling
    try:
        processed_data = user_data.copy()
        processed_data["processed"] = True
        return processed_data
    except Exception as e:
        return {"error": str(e)}
    
    # This line should never be reached
    return None
'''
    
    # Write sample file
    with open('demo_user_processor.py', 'w') as f:
        f.write(sample_code)
    
    print("📝 Created demo file: demo_user_processor.py")
    
    # Create mock coverage data (simulating 60% coverage)
    total_lines = len(sample_code.split('\n'))
    covered_lines = int(total_lines * 0.6)
    uncovered_lines = list(range(covered_lines + 1, total_lines + 1))
    
    coverage_data = CoverageData(
        total_lines=total_lines,
        covered_lines=covered_lines,
        coverage_percentage=60.0,
        uncovered_lines=uncovered_lines,
        file_path='demo_user_processor.py',
        language='py'
    )
    
    print(f"📊 Mock coverage data: {coverage_data.coverage_percentage:.1f}%")
    
    # Generate suggestions
    suggestions = agent._generate_test_suggestions(
        coverage_data, 'demo_user_processor.py', 'py'
    )
    
    print(f"💡 Generated {len(suggestions)} test suggestions")
    
    # Display suggestions
    for i, suggestion in enumerate(suggestions, 1):
        print(f"\n{i}. {suggestion.description}")
        print(f"   Type: {suggestion.suggestion_type}")
        print(f"   Priority: {suggestion.priority}")
        if suggestion.code_snippet:
            print(f"   Code: {suggestion.code_snippet}")
    
    # Generate report
    report = agent._generate_coverage_report([coverage_data], suggestions)
    
    print(f"\n📋 Recommendations:")
    for rec in report['recommendations']:
        print(f"   • {rec}")
    
    # Clean up
    import os
    if os.path.exists('demo_user_processor.py'):
        os.remove('demo_user_processor.py')
        print("\n🧹 Cleaned up demo file")
    
    print("\n✅ Demo completed!")

if __name__ == "__main__":
    # Run demo if no arguments
    if len(sys.argv) == 1:
        run_demo()
    else:
        # Run tests
        unittest.main()
