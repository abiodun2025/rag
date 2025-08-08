#!/usr/bin/env python3
"""
CLI for Test Coverage & Suggestions Agent

Usage:
    python3 test_coverage_cli.py analyze-pr <pr_number> <owner> <repo>
    python3 test_coverage_cli.py analyze-file <file_path>
    python3 test_coverage_cli.py generate-suggestions <file_path>
    python3 test_coverage_cli.py interactive
"""

import sys
import json
import argparse
from pathlib import Path
from agent.test_coverage_agent import TestCoverageAgent

def print_banner():
    """Print the CLI banner."""
    print("🧪 Test Coverage & Suggestions Agent CLI")
    print("=" * 50)
    print("📊 Monitors test coverage and suggests missing test cases")
    print("🔧 Supports: JaCoCo, Istanbul, Python coverage, Go test")
    print("🤖 LLM-enhanced intelligent suggestions")
    print("=" * 50)

def analyze_pr(pr_number: int, owner: str, repo: str):
    """Analyze test coverage for a pull request."""
    print(f"🔍 Analyzing PR #{pr_number} in {owner}/{repo}")
    
    agent = TestCoverageAgent()
    report = agent.analyze_pr_coverage(pr_number, owner, repo)
    
    if "error" in report:
        print(f"❌ Error: {report['error']}")
        return
    
    print_coverage_report(report)

def analyze_file(file_path: str):
    """Analyze test coverage for a specific file."""
    print(f"🔍 Analyzing file: {file_path}")
    
    agent = TestCoverageAgent()
    
    # Detect language
    language = agent._detect_language(file_path)
    print(f"📝 Detected language: {language}")
    
    if language not in agent.supported_languages:
        print(f"❌ Unsupported language: {language}")
        return
    
    # Analyze coverage
    coverage_data = agent._analyze_file_coverage(file_path, language)
    if not coverage_data:
        print("❌ No coverage data found for this file")
        print("💡 Make sure to run tests with coverage enabled")
        return
    
    # Generate suggestions
    suggestions = agent._generate_test_suggestions(coverage_data, file_path, language)
    
    # Create a simple report
    report = agent._generate_coverage_report([coverage_data], suggestions)
    print_coverage_report(report)

def generate_suggestions(file_path: str):
    """Generate test suggestions for a file."""
    print(f"💡 Generating test suggestions for: {file_path}")
    
    agent = TestCoverageAgent()
    
    # Create mock coverage data for demonstration
    from agent.test_coverage_agent import CoverageData
    
    # Read the file to get line count
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
            total_lines = len(lines)
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        return
    
    # Create mock coverage data (50% coverage for demo)
    covered_lines = total_lines // 2
    uncovered_lines = list(range(covered_lines + 1, total_lines + 1))
    
    coverage_data = CoverageData(
        total_lines=total_lines,
        covered_lines=covered_lines,
        coverage_percentage=50.0,
        uncovered_lines=uncovered_lines,
        file_path=file_path,
        language=agent._detect_language(file_path)
    )
    
    # Generate suggestions
    suggestions = agent._generate_test_suggestions(coverage_data, file_path, coverage_data.language)
    
    print_suggestions(suggestions)

def interactive_mode():
    """Interactive mode for the CLI."""
    print_banner()
    print("\n🎯 Interactive Mode")
    print("Type 'help' for commands or 'exit' to quit")
    print("-" * 30)
    
    agent = TestCoverageAgent()
    
    while True:
        try:
            command = input("\n🤖 Test Coverage Agent> ").strip()
            
            if command.lower() in ['exit', 'quit', 'q']:
                print("👋 Goodbye!")
                break
            elif command.lower() == 'help':
                print_help()
            elif command.startswith('analyze-pr '):
                parts = command.split()
                if len(parts) >= 4:
                    try:
                        pr_number = int(parts[1])
                        owner = parts[2]
                        repo = parts[3]
                        analyze_pr(pr_number, owner, repo)
                    except ValueError:
                        print("❌ Invalid PR number")
                else:
                    print("❌ Usage: analyze-pr <pr_number> <owner> <repo>")
            elif command.startswith('analyze-file '):
                file_path = command.split(' ', 1)[1]
                if Path(file_path).exists():
                    analyze_file(file_path)
                else:
                    print(f"❌ File not found: {file_path}")
            elif command.startswith('suggestions '):
                file_path = command.split(' ', 1)[1]
                if Path(file_path).exists():
                    generate_suggestions(file_path)
                else:
                    print(f"❌ File not found: {file_path}")
            elif command == 'demo':
                run_demo(agent)
            else:
                print("❌ Unknown command. Type 'help' for available commands.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def run_demo(agent):
    """Run a demo of the test coverage agent."""
    print("\n🎬 Running Demo...")
    
    # Create a demo file
    demo_file = "demo_function.py"
    demo_content = '''def calculate_discount(price, discount_percent, is_member=False):
    """Calculate discount for a product."""
    if price <= 0:
        return 0
    
    if discount_percent < 0 or discount_percent > 100:
        return price
    
    discount = price * (discount_percent / 100)
    
    if is_member:
        discount *= 1.1  # 10% extra for members
    
    return max(0, price - discount)

def validate_user_input(username, email, age):
    """Validate user input."""
    if not username or len(username) < 3:
        return False, "Username too short"
    
    if '@' not in email:
        return False, "Invalid email"
    
    if age < 0 or age > 150:
        return False, "Invalid age"
    
    return True, "Valid input"
'''
    
    with open(demo_file, 'w') as f:
        f.write(demo_content)
    
    print(f"📝 Created demo file: {demo_file}")
    
    # Analyze the demo file
    analyze_file(demo_file)
    
    # Clean up
    Path(demo_file).unlink()
    print(f"🧹 Cleaned up demo file")

def print_coverage_report(report):
    """Print a formatted coverage report."""
    print("\n📊 Coverage Report")
    print("=" * 50)
    
    overall = report.get('overall_coverage', {})
    print(f"🎯 Overall Coverage: {overall.get('percentage', 0):.1f}%")
    print(f"📈 Total Lines: {overall.get('total_lines', 0)}")
    print(f"✅ Covered Lines: {overall.get('covered_lines', 0)}")
    print(f"❌ Uncovered Lines: {overall.get('uncovered_lines', 0)}")
    
    # File coverage
    file_coverage = report.get('file_coverage', [])
    if file_coverage:
        print(f"\n📁 File Coverage:")
        for file_data in file_coverage:
            print(f"   {file_data['file_path']}: {file_data['coverage_percentage']:.1f}%")
    
    # Suggestions
    suggestions = report.get('suggestions', {})
    if suggestions['total'] > 0:
        print(f"\n💡 Test Suggestions:")
        print(f"   🔴 High Priority: {suggestions['high_priority']}")
        print(f"   🟡 Medium Priority: {suggestions['medium_priority']}")
        print(f"   🟢 Low Priority: {suggestions['low_priority']}")
        
        # Show top suggestions
        details = suggestions.get('details', [])
        if details:
            print(f"\n🎯 Top Suggestions:")
            for i, suggestion in enumerate(details[:5], 1):
                print(f"   {i}. {suggestion['description']}")
                print(f"      File: {suggestion['file_path']}:{suggestion['line_number']}")
                print(f"      Type: {suggestion['type']} | Priority: {suggestion['priority']}")
                if suggestion['code_snippet']:
                    print(f"      Code: {suggestion['code_snippet']}")
                print()
    
    # Recommendations
    recommendations = report.get('recommendations', [])
    if recommendations:
        print(f"📋 Recommendations:")
        for rec in recommendations:
            print(f"   • {rec}")
    
    print("=" * 50)

def print_suggestions(suggestions):
    """Print test suggestions."""
    if not suggestions:
        print("✅ No suggestions needed - good coverage!")
        return
    
    print(f"\n💡 Test Suggestions ({len(suggestions)} total)")
    print("=" * 50)
    
    # Group by priority
    high_priority = [s for s in suggestions if s.priority == 'high']
    medium_priority = [s for s in suggestions if s.priority == 'medium']
    low_priority = [s for s in suggestions if s.priority == 'low']
    
    if high_priority:
        print(f"\n🔴 High Priority ({len(high_priority)}):")
        for i, suggestion in enumerate(high_priority, 1):
            print(f"   {i}. {suggestion.description}")
            if suggestion.line_number > 0:
                print(f"      Line {suggestion.line_number}: {suggestion.code_snippet}")
    
    if medium_priority:
        print(f"\n🟡 Medium Priority ({len(medium_priority)}):")
        for i, suggestion in enumerate(medium_priority, 1):
            print(f"   {i}. {suggestion.description}")
            if suggestion.line_number > 0:
                print(f"      Line {suggestion.line_number}: {suggestion.code_snippet}")
    
    if low_priority:
        print(f"\n🟢 Low Priority ({len(low_priority)}):")
        for i, suggestion in enumerate(low_priority, 1):
            print(f"   {i}. {suggestion.description}")
            if suggestion.line_number > 0:
                print(f"      Line {suggestion.line_number}: {suggestion.code_snippet}")
    
    print("=" * 50)

def print_help():
    """Print help information."""
    print("\n📖 Available Commands:")
    print("   analyze-pr <pr_number> <owner> <repo>  - Analyze PR coverage")
    print("   analyze-file <file_path>               - Analyze file coverage")
    print("   suggestions <file_path>                - Generate test suggestions")
    print("   demo                                   - Run demo")
    print("   help                                   - Show this help")
    print("   exit                                   - Exit the CLI")
    print("\n💡 Examples:")
    print("   analyze-pr 123 owner repo")
    print("   analyze-file src/main.py")
    print("   suggestions tests/test_file.py")

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Test Coverage & Suggestions Agent CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 test_coverage_cli.py analyze-pr 123 owner repo
  python3 test_coverage_cli.py analyze-file src/main.py
  python3 test_coverage_cli.py generate-suggestions tests/test_file.py
  python3 test_coverage_cli.py interactive
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Analyze PR command
    pr_parser = subparsers.add_parser('analyze-pr', help='Analyze PR coverage')
    pr_parser.add_argument('pr_number', type=int, help='Pull request number')
    pr_parser.add_argument('owner', help='Repository owner')
    pr_parser.add_argument('repo', help='Repository name')
    
    # Analyze file command
    file_parser = subparsers.add_parser('analyze-file', help='Analyze file coverage')
    file_parser.add_argument('file_path', help='Path to the file to analyze')
    
    # Generate suggestions command
    suggestions_parser = subparsers.add_parser('generate-suggestions', help='Generate test suggestions')
    suggestions_parser.add_argument('file_path', help='Path to the file')
    
    # Interactive command
    subparsers.add_parser('interactive', help='Start interactive mode')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    print_banner()
    
    if args.command == 'analyze-pr':
        analyze_pr(args.pr_number, args.owner, args.repo)
    elif args.command == 'analyze-file':
        analyze_file(args.file_path)
    elif args.command == 'generate-suggestions':
        generate_suggestions(args.file_path)
    elif args.command == 'interactive':
        interactive_mode()

if __name__ == "__main__":
    main()
